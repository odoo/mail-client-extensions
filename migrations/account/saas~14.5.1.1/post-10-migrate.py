# -*- coding: utf-8 -*-


def migrate(cr, version):
    # ==========================================================================
    # Zero tax line creation
    # ==========================================================================
    cr.execute(
        """
            SELECT DISTINCT line.move_id
              INTO TEMPORARY TABLE move_ids_to_exclude
              FROM account_move_line line
              JOIN account_tax tax ON tax.id = line.tax_line_id
             WHERE tax.amount_type != 'group'
               AND tax.amount = 0.0
        """
    )

    # Handles regular 0% taxes.
    cr.execute(
        """
        INSERT INTO account_move_line (move_id, move_name, date, parent_state, journal_id, company_id,
                                       company_currency_id, account_id, account_root_id, sequence, name,
                                       partner_id, analytic_account_id, reconciled, blocked,
                                       currency_id, tax_repartition_line_id, tax_line_id, tax_group_id, exclude_from_invoice_tab,
                                       tax_base_amount)
        SELECT move.id, move.name, base_line.date, base_line.parent_state, base_line.journal_id, base_line.company_id,
               base_line.company_currency_id, account.id, account.root_id, 10, COALESCE(NULLIF(ir_translation.value, ''), tax.name),
               base_line.partner_id, CASE WHEN tax.analytic THEN base_line.analytic_account_id END, account.reconcile, FALSE,
               base_line.currency_id, atrl.id, tax.id, tax.tax_group_id, TRUE,
               CASE
                   WHEN
                           (tax.type_tax_use = 'sale' AND atrl.invoice_tax_id IS NOT NULL)
                       OR
                           (tax.type_tax_use = 'purchase' AND atrl.refund_tax_id IS NOT NULL)
                   THEN -SUM(base_line.balance)
                   ELSE SUM(base_line.balance) END
        FROM account_move_line_account_tax_rel rel
        JOIN account_tax tax ON rel.account_tax_id = tax.id AND tax.amount_type != 'group' AND tax.amount = 0.0
        JOIN account_move_line base_line ON base_line.id = rel.account_move_line_id
        JOIN account_move move ON base_line.move_id = move.id
        JOIN account_tax_repartition_line atrl ON
            (
                (move.move_type IN ('out_refund', 'in_refund') AND atrl.refund_tax_id = tax.id)
            OR
                (move.move_type NOT IN ('out_refund', 'in_refund') AND atrl.invoice_tax_id = tax.id)
            )
            AND repartition_type = 'tax'
        JOIN account_account account ON tax.tax_exigibility = 'on_payment'
            AND account.id = tax.cash_basis_transition_account_id OR account.id = COALESCE(atrl.account_id, base_line.account_id)
        JOIN res_company ON move.company_id = res_company.id
        JOIN res_partner ON res_company.partner_id = res_partner.id
        LEFT JOIN ir_translation ON ir_translation.name = 'account.tax,name'
            AND ir_translation.res_id = tax.id AND ir_translation.type = 'model' AND ir_translation.lang = res_partner.lang
        WHERE NOT EXISTS (SELECT 1 FROM move_ids_to_exclude WHERE move_ids_to_exclude.move_id = base_line.move_id)
        GROUP BY base_line.company_id, base_line.company_currency_id, base_line.currency_id, base_line.partner_id,
                 base_line.account_id, base_line.date, base_line.parent_state, move.id, base_line.journal_id,
                 COALESCE(NULLIF(ir_translation.value, ''), tax.name), tax.tax_exigibility, tax.type_tax_use, tax.id,
                 tax.tax_group_id, tax.cash_basis_transition_account_id, atrl.id, account.id,
                 CASE WHEN tax.analytic THEN base_line.analytic_account_id END

    """
    )

    # Handle taxes with amount_type = 'group'. A line should be created for each children tax with a 0%
    cr.execute(
        """
        INSERT INTO account_move_line (move_id, move_name, date, parent_state, journal_id, company_id,
                                       company_currency_id, account_id, account_root_id, sequence, name,
                                       partner_id, analytic_account_id, reconciled, blocked,
                                       currency_id, tax_repartition_line_id, tax_line_id, tax_group_id, exclude_from_invoice_tab,
                                       tax_base_amount,
                                       group_tax_id)
        SELECT move.id, move.name, base_line.date, base_line.parent_state, base_line.journal_id, base_line.company_id,
               base_line.company_currency_id, account.id, account.root_id, 10, COALESCE(NULLIF(ir_translation.value, ''), tax.name),
               base_line.partner_id, CASE WHEN tax.analytic THEN base_line.analytic_account_id END, account.reconcile, FALSE,
               base_line.currency_id, atrl.id, tax.id, tax.tax_group_id, TRUE,
               CASE
                   WHEN
                           (tax.type_tax_use = 'sale' OR (tax.type_tax_use = 'none' AND parent_tax.type_tax_use = 'sale'))
                           AND atrl.invoice_tax_id IS NOT NULL
                       OR
                           (tax.type_tax_use = 'purchase' OR (tax.type_tax_use = 'none' AND parent_tax.type_tax_use = 'purchase'))
                           AND atrl.refund_tax_id IS NOT NULL
                   THEN -SUM(base_line.balance)
                   ELSE SUM(base_line.balance) END,
               parent_tax.id
        FROM account_move_line_account_tax_rel rel
        JOIN account_tax_filiation_rel ON account_tax_filiation_rel.parent_tax = rel.account_tax_id
        JOIN account_tax parent_tax ON parent_tax.id = account_tax_filiation_rel.parent_tax AND parent_tax.amount_type = 'group'
        JOIN account_tax tax ON tax.id = account_tax_filiation_rel.child_tax AND tax.amount_type != 'group' AND tax.amount = 0.0
        JOIN account_move_line base_line ON base_line.id = rel.account_move_line_id
        JOIN account_move move ON base_line.move_id = move.id
        JOIN account_tax_repartition_line atrl ON
            (
                (move.move_type IN ('out_refund', 'in_refund') AND atrl.refund_tax_id = tax.id)
            OR
                (move.move_type NOT IN ('out_refund', 'in_refund') AND atrl.invoice_tax_id = tax.id)
            )
            AND repartition_type = 'tax'
        JOIN account_account account ON tax.tax_exigibility = 'on_payment'
            AND account.id = tax.cash_basis_transition_account_id OR account.id = COALESCE(atrl.account_id, base_line.account_id)
        JOIN res_company ON move.company_id = res_company.id
        JOIN res_partner ON res_company.partner_id = res_partner.id
        LEFT JOIN ir_translation ON ir_translation.name = 'account.tax,name'
            AND ir_translation.res_id = tax.id AND ir_translation.type = 'model' AND ir_translation.lang = res_partner.lang
        WHERE NOT EXISTS (SELECT 1 FROM move_ids_to_exclude WHERE move_ids_to_exclude.move_id = base_line.move_id)
        GROUP BY base_line.company_id, base_line.company_currency_id, base_line.currency_id, base_line.partner_id, move.id,
                 base_line.account_id, base_line.date, base_line.parent_state, base_line.journal_id,
                 COALESCE(NULLIF(ir_translation.value, ''), tax.name), tax.tax_exigibility, tax.type_tax_use, tax.id,
                 tax.tax_group_id, tax.cash_basis_transition_account_id, parent_tax.type_tax_use, parent_tax.id, atrl.id,
                 account.id, CASE WHEN tax.analytic THEN base_line.analytic_account_id END
    """
    )
