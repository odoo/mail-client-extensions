import logging
import textwrap

from odoo.upgrade import util

_logger = logging.getLogger("odoo.upgrade.account/saas~18.3")


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

    _logger.info("Updating account_bank_statement.currency_id")
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

    _logger.info("Updating account_account.reconcile")
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

    """
    This case was mechanically supported, but we know the use case
    we implemented it for actually ended up not being covered by this,
    and now makes use of branches for that.
    So, we have very good reasons to believe no one is using this.
    This check in the script is just there to ensure we can be directly
    aware if this assumption proves incorrect.
    Then, we'll see case by case (=> contact oco).
    It should anyway touch very very few people.
    """
    cr.execute(
        """
        SELECT c.code,
               ARRAY_AGG(fp.name ORDER BY fp.id),
               ARRAY_AGG(fp.foreign_vat ORDER BY fp.id)
          FROM account_fiscal_position fp
          JOIN res_country c
            ON fp.country_id = c.id
         WHERE fp.foreign_vat IS NOT NULL
      GROUP BY c.id
        HAVING COUNT(DISTINCT fp.foreign_vat) > 1
        """
    )

    if cr.rowcount:
        fps_by_country = "\n".join(
            f"- {country_code}: " + ", ".join(f"{name} (VAT: {vat})" for name, vat in zip(names, vats))
            for country_code, names, vats in cr.fetchall()
        )
        raise util.UpgradeError(
            textwrap.dedent(
                f"""
                Multiple fiscal positions with different foreign VAT numbers exist for the same country in your database.
                This configuration is not supported anymore.
                Fiscal positions by country:
                {fps_by_country}
                """
            )
        )

    _logger.info("Updating account.report default_opening_date_filter")
    util.change_field_selection_values(
        cr,
        "account.report",
        "default_opening_date_filter",
        {
            "this_tax_period": "this_return_period",
            "previous_tax_period": "previous_return_period",
        },
    )

    util.change_field_selection_values(
        cr,
        "account.report.expression",
        "date_scope",
        {
            "previous_tax_period": "previous_return_period",
        },
    )

    util.remove_field(cr, "account.report.external.value", "foreign_vat_fiscal_position_id")
    util.rename_field(cr, "account.report", "filter_fiscal_position", "allow_foreign_vat")

    util.invert_boolean_field(cr, "account.account", "deprecated", "active")
    util.remove_field(cr, "account.account", "allowed_journal_ids")

    # Fiscal Position Tax mapping
    _logger.info("Fiscal position tax mapping")
    util.create_m2m(cr, "account_fiscal_position_account_tax_rel", "account_tax", "account_fiscal_position")
    cr.execute(
        """
               WITH domestic_fiscal_positions AS (
                    SELECT DISTINCT ON (fp.company_id)
                           fp.company_id,
                           fp.id as position_id
                      FROM account_fiscal_position fp
                INNER JOIN res_company c
                        ON fp.company_id = c.id
                     WHERE fp.country_id = c.account_fiscal_country_id
                  ORDER BY fp.company_id, fp.sequence ASC, fp.id ASC
               )
        INSERT INTO account_fiscal_position_account_tax_rel(account_tax_id, account_fiscal_position_id)
             SELECT tax_dest_id, position_id
               FROM account_fiscal_position_tax
              WHERE tax_dest_id IS NOT NULL
                AND position_id IS NOT NULL
              UNION
             SELECT tax_src_id, domestic_fiscal_positions.position_id
               FROM account_fiscal_position_tax afpt
               JOIN domestic_fiscal_positions
                 ON afpt.company_id = domestic_fiscal_positions.company_id
              WHERE tax_src_id IS NOT NULL
                AND domestic_fiscal_positions.position_id IS NOT NULL
        """
    )

    util.create_m2m(cr, "account_tax_alternatives", "account_tax", "account_tax", "dest_tax_id", "src_tax_id")
    cr.execute(
        """
        INSERT INTO account_tax_alternatives(dest_tax_id, src_tax_id)
             SELECT DISTINCT tax_dest_id, tax_src_id
               FROM account_fiscal_position_tax
              WHERE tax_dest_id IS NOT NULL
        """
    )

    util.remove_model(cr, "account.fiscal.position.tax")

    # -= bank reco widget revamped =-
    _logger.info("Migrate the (Rule to suggest counterpart entry) models.")
    cr.execute(
        util.format_query(
            cr,
            """
             UPDATE account_reconcile_model
                SET match_label = COALESCE(match_label, match_note, {match_transaction_details}),
                    match_label_param = COALESCE(match_label_param, match_note_param, {match_transaction_details_param})
              WHERE rule_type = 'writeoff_suggestion'
            """,
            match_transaction_details="match_transaction_details"
            if util.column_exists(cr, "account_reconcile_model", "match_transaction_details")
            else util.SQLStr("NULL"),
            match_transaction_details_param="match_transaction_details_param"
            if util.column_exists(cr, "account_reconcile_model", "match_transaction_details_param")
            else util.SQLStr("NULL"),
        )
    )

    util.remove_field(cr, "account.reconcile.model.line", "rule_type")
    util.remove_field(cr, "account.reconcile.model.line", "journal_id")
    util.remove_field(cr, "account.reconcile.model.line", "allow_payment_tolerance")
    util.remove_field(cr, "account.reconcile.model.line", "payment_tolerance_param")
    util.remove_field(cr, "account.reconcile.model", "matching_order")
    util.remove_field(cr, "account.reconcile.model", "match_note")
    util.remove_field(cr, "account.reconcile.model", "match_note_param")
    util.remove_field(cr, "account.reconcile.model", "match_transaction_details")
    util.remove_field(cr, "account.reconcile.model", "match_transaction_details_param")
    util.remove_field(cr, "account.reconcile.model", "match_text_location_label")
    util.remove_field(cr, "account.reconcile.model", "match_text_location_note")
    util.remove_field(cr, "account.reconcile.model", "match_text_location_reference")
    util.remove_field(cr, "account.reconcile.model", "match_same_currency")
    util.remove_field(cr, "account.reconcile.model", "match_partner_category_ids")
    util.remove_field(cr, "account.reconcile.model", "match_partner")
    util.remove_field(cr, "account.reconcile.model", "allow_payment_tolerance")
    util.remove_field(cr, "account.reconcile.model", "payment_tolerance_param")
    util.remove_field(cr, "account.reconcile.model", "payment_tolerance_type")
    util.remove_field(cr, "account.reconcile.model", "counterpart_type")

    _logger.info("Each of the partner_mapping lines should be a dedicated reco model")
    util.explode_execute(
        cr,
        r"""
        INSERT INTO account_reconcile_model(
                    sequence, company_id, journal_id, auto_reconcile,
                    match_label, match_label_param,
                    name, rule_type, active
                    )
             SELECT 100, model.company_id, model.journal_id, 't',
                    'contains', COALESCE(map.payment_ref_regex, map.narration_regex),
                    jsonb_build_object('en_US', 'partner\_mapping\_' || map.id), 'writeoff_button', 't'
               FROM account_reconcile_model_partner_mapping map
               JOIN account_reconcile_model model
                 ON map.model_id = model.id
              WHERE model.rule_type != 'writeoff_button'
        """,
        table="account_reconcile_model",
        alias="model",
    )
    _logger.info("assign matching_journal_ids")
    cr.execute(
        r"""
        INSERT INTO account_journal_account_reconcile_model_rel(account_reconcile_model_id, account_journal_id)
             SELECT new_model.id, m2m.account_journal_id
               FROM account_journal_account_reconcile_model_rel m2m
               JOIN account_reconcile_model parent_model
                 ON m2m.account_reconcile_model_id = parent_model.id
               JOIN account_reconcile_model_partner_mapping map
                 ON map.model_id = parent_model.id
               JOIN account_reconcile_model new_model
                 ON (new_model.name::TEXT like '%' || 'partner\_mapping\_' || map.id::TEXT || '%')
        ON CONFLICT DO NOTHING
        """
    )
    _logger.info("assign the right partner by creating a counterpart line with map.partner_id and no account")
    util.create_column(cr, "account_reconcile_model_line", "partner_id", "int")
    util.explode_execute(
        cr,
        r"""
        INSERT INTO account_reconcile_model_line(model_id, partner_id, sequence, amount_type, amount_string, company_id)
             SELECT model.id, map.partner_id, 10, 'percentage', '100', model.company_id
               FROM account_reconcile_model model
               JOIN account_reconcile_model_partner_mapping map
                 ON (model.name::TEXT like '%' || 'partner\_mapping\_' || map.id::TEXT || '%')
              WHERE model.name::TEXT like '%' || 'partner\_mapping\_' || '%'
        """,
        table="account_reconcile_model",
        alias="model",
    )

    _logger.info("invoice_matching is now hardcoded")
    cr.execute("CREATE INDEX ON account_move_line(reconcile_model_id) WHERE reconcile_model_id IS NOT NULL")
    cr.commit()
    util.explode_execute(
        cr,
        """
         DELETE FROM account_reconcile_model
         WHERE rule_type IN ('invoice_matching')
        """,
        table="account_reconcile_model",
    )

    util.remove_field(cr, "account.reconcile.model", "rule_type")
    util.remove_field(cr, "account.reconcile.model", "journal_id")
    util.remove_field(cr, "account.reconcile.model", "number_entries")
    util.remove_field(cr, "account.reconcile.model", "past_months_limit")
    util.remove_field(cr, "account.reconcile.model", "number_entries")
    util.remove_field(cr, "account.reconcile.model", "decimal_separator")
    util.remove_field(cr, "account.reconcile.model", "show_decimal_separator")
    util.remove_field(cr, "account.reconcile.model", "partner_mapping_line_ids")
    util.remove_field(cr, "account.reconcile.model", "to_check")
    util.remove_model(cr, "account.reconcile.model.partner.mapping")
    util.alter_column_type(
        cr,
        "account_reconcile_model",
        "auto_reconcile",
        "varchar",
        using="CASE {0} WHEN True THEN 'auto_reconcile' ELSE 'manual' END",
    )
    util.rename_field(cr, "account.reconcile.model", "auto_reconcile", "trigger")

    util.rename_field(cr, "res.company", "check_account_audit_trail", "restrictive_audit_trail")
    util.rename_field(cr, "res.config.settings", "check_account_audit_trail", "restrictive_audit_trail")
    util.rename_field(cr, "mail.message", "account_audit_log_activated", "account_audit_log_restricted")
