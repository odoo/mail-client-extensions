from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_journal", "incoming_einvoice_notification_email", "varchar")
    cr.execute(
        """
        UPDATE account_journal AS j
           SET incoming_einvoice_notification_email = c.email
          FROM res_company AS c
         WHERE c.id = j.company_id
           AND j.type = 'purchase';
        """
    )

    util.create_column(cr, "account_bank_statement", "currency_id", "integer")
    util.explode_execute(
        cr,
        """
         UPDATE account_bank_statement AS s_up
           SET currency_id = COALESCE(j.currency_id, c.currency_id)
          FROM account_bank_statement AS s
     LEFT JOIN account_journal AS j
            ON (s.journal_id = j.id)
     LEFT JOIN res_company AS c
            ON (j.company_id = c.id)
         WHERE s_up.id = s.id
        """,
        table="account_bank_statement",
        alias="s_up",
    )

    util.remove_field(cr, "res.partner", "debit_limit")
    util.remove_field(cr, "res.partner", "journal_item_count")

    util.remove_field(cr, "res.partner", "invoice_warn")
    util.remove_field(cr, "res.partner", "invoice_warn_msg")
    util.remove_field(cr, "res.config.settings", "group_warning_account")
    util.remove_group(cr, "account.group_warning_account")
    util.remove_field(cr, "res.config.settings", "module_account_bank_statement_import_ofx")
    util.remove_field(cr, "res.config.settings", "module_account_bank_statement_import_csv")
    util.remove_field(cr, "res.config.settings", "module_account_bank_statement_import_camt")
    util.remove_field(cr, "account.full.reconcile", "exchange_move_id")

    cr.execute(
        """
        UPDATE account_account
           SET reconcile = TRUE
          FROM account_tax
         WHERE account_account.id = account_tax.cash_basis_transition_account_id
           AND account_account.reconcile IS NOT TRUE
     RETURNING account_account.id
        """
    )
    account_ids = [row[0] for row in cr.fetchall()]
    if account_ids:

        # Copy paste of account.account _toggle_reconcile_to_true
        query = cr.mogrify(
            """
            UPDATE account_move_line
               SET reconciled = CASE WHEN debit = 0 AND credit = 0 AND amount_currency = 0 THEN true ELSE false END,
                   amount_residual = debit - credit,
                   amount_residual_currency = amount_currency
             WHERE full_reconcile_id IS NULL
               AND account_id IN %s
            """,
            [tuple(account_ids)],
        ).decode()
        util.explode_execute(cr, query, table="account_move_line")
