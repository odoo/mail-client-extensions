# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces

    util.create_column(cr, "account_account", "root_id", "int4")
    cr.execute(
        """
        UPDATE account_account
           SET root_id = ASCII(code) * 1000 + ASCII(SUBSTRING(code,2,1))
    """
    )

    util.rename_field(cr, "account.journal.group", "account_journal_ids", "excluded_journal_ids")
    # field has been reverted, it not contains the journals to *not* use in the group
    if util.table_exists(cr, "account_journal_account_journal_group_rel"):
        cr.execute(
            """
            WITH group_journals AS (
                DELETE
                  FROM account_journal_account_journal_group_rel
             RETURNING account_journal_group_id, account_journal_id
            )
            INSERT INTO account_journal_account_journal_group_rel(account_journal_group_id, account_journal_id)
                 SELECT g.id, j.id
                   FROM account_journal_group g, account_journal j
                  WHERE g.id IN (SELECT account_journal_group_id FROM group_journals)
                    AND g.company_id = j.company_id
                 EXCEPT
                 SELECT account_journal_group_id, account_journal_id
                   FROM group_journals
        """
        )

    util.create_column(cr, "account_journal", "restrict_mode_hash_table", "boolean")
    util.create_column(cr, "account_journal", "post_at", "varchar")
    util.create_column(cr, "account_journal", "secure_sequence_id", "int4")
    cr.execute(
        """
        UPDATE account_journal
           SET post_at = CASE WHEN post_at_bank_rec THEN 'bank_rec' ELSE 'pay_val' END
    """
    )
    util.remove_field(cr, "account.journal", "belongs_to_company")
    util.remove_field(cr, "account.journal", "update_posted")

    # copy company data from l10n_fr_certification module
    if util.column_exists(cr, "res_company", "l10n_fr_secure_sequence_id"):
        cr.execute(
            """
            UPDATE account_journal j
               SET secure_sequence_id = c.l10n_fr_secure_sequence_id,
                   restrict_mode_hash_table = true
              FROM res_company c
             WHERE c.id = j.company_id
               AND c.l10n_fr_secure_sequence_id IS NOT NULL
               AND j.type not in ('cash','bank')
    """
        )

    # no more 'adjustment' taxes
    cr.execute("UPDATE account_tax SET active=false, type_tax_use='none' WHERE type_tax_use = 'adjustment'")
    cr.execute(
        """
        WITH gone AS (
            DELETE FROM account_tax_template
                  WHERE type_tax_use = 'adjustment'
              RETURNING id
        )
        DELETE FROM ir_model_data
              WHERE model = 'account.tax.template'
                AND res_id IN (SELECT id FROM gone)
    """
    )

    util.create_column(cr, "account_bank_statement_line", "transaction_type", "varchar")

    util.rename_field(cr, "account.move", *eb("invoice_{vendor,partner}_display_name"))
    util.rename_field(cr, "account.move", *eb("invoice_{vendor,partner}_icon"))
    util.rename_field(cr, "account.move", *eb("invoice_has_matching_su{ps,sp}ense_amount"))

    # steal fields from `l10n_fr_certification`
    changes = {
        "l10n_fr_secure_sequence_number": ("secure_sequence_number", "int4"),
        "l10n_fr_hash": ("inalterable_hash", "varchar"),
        "l10n_fr_string_to_hash": ("string_to_hash", None),
    }
    for old, (field, ftype) in changes.items():
        util.move_field_to_module(cr, "account.move", old, "l10n_fr_certification", "account")
        util.rename_field(cr, "account.move", old, field)
        if ftype and not util.column_exists(cr, "account_move", field):
            util.create_column(cr, "account_move", field, ftype)

    util.create_column(cr, "account_move_line", "account_root_id", "int4")
    util.create_column(cr, "account_move_line", "tax_group_id", "int4")
    query = """
            UPDATE account_move_line l
               SET account_root_id = a.root_id
              FROM account_account a
             WHERE a.id = l.account_id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_move_line", alias="l"))

    query = """
            UPDATE account_move_line l
               SET tax_group_id = t.tax_group_id
             FROM account_tax t
            WHERE t.id = l.tax_line_id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_move_line", alias="l"))

    for suffix in {"", "_template"}:
        table = "account_reconcile_model" + suffix
        util.create_column(cr, table, "match_note", "varchar")
        util.create_column(cr, table, "match_note_param", "varchar")
        util.create_column(cr, table, "match_transaction_type", "varchar")
        util.create_column(cr, table, "match_transaction_type_param", "varchar")
        util.create_column(cr, table, "amount_from_label_regex", "varchar")
        util.create_column(cr, table, "decimal_separator", "varchar")
        util.create_column(cr, table, "second_amount_from_label_regex", "varchar")

        cr.execute(
            r"""
            UPDATE {}
               SET amount_from_label_regex = '([\d\.,]+)',
                   second_amount_from_label_regex = '([\d\.,]+)'
        """.format(
                table
            )
        )

    cr.execute(
        """
        UPDATE account_reconcile_model r
           SET decimal_separator = l.decimal_point
          FROM res_users u, res_partner p, res_lang l
         WHERE u.id = r.create_uid
           AND p.id = u.partner_id
           AND l.code = p.lang
    """
    )

    util.create_column(cr, "account_account", "root_id", "int4")
    cr.execute(
        """
        UPDATE account_account
           SET root_id=ASCII(code) * 1000 + ASCII(SUBSTRING(code,2,1))
         WHERE code IS NOT NULL
           AND root_id IS NULL
    """
    )
    util.create_column(cr, "account_account_template", "root_id", "int4")

    util.create_column(cr, "account_chart_template", "default_cash_difference_income_account_id", "int4")
    util.create_column(cr, "account_chart_template", "default_cash_difference_expense_account_id", "int4")
    util.create_column(cr, "account_chart_template", "default_pos_receivable_account_id", "int4")

    util.create_column(cr, "res_company", "default_cash_difference_income_account_id", "int4")
    util.create_column(cr, "res_company", "default_cash_difference_expense_account_id", "int4")
    util.create_column(cr, "res_company", "account_default_pos_receivable_account_id", "int4")
    util.create_column(cr, "res_company", "expense_accrual_account_id", "int4")
    util.create_column(cr, "res_company", "revenue_accrual_account_id", "int4")
    util.create_column(cr, "res_company", "accrual_default_journal_id", "int4")
    util.remove_field(cr, "res.company", "overdue_msg")

    cr.execute("ALTER TABLE account_fiscal_position_template ALTER COLUMN zip_from TYPE varchar")
    cr.execute("ALTER TABLE account_fiscal_position_template ALTER COLUMN zip_to TYPE varchar")
    cr.execute("UPDATE account_fiscal_position_template SET zip_from = NULL WHERE zip_from = '0'")
    cr.execute("UPDATE account_fiscal_position_template SET zip_to = NULL WHERE zip_to = '0'")

    cr.execute("ALTER TABLE account_fiscal_position ALTER COLUMN zip_from TYPE varchar")
    cr.execute("ALTER TABLE account_fiscal_position ALTER COLUMN zip_to TYPE varchar")
    cr.execute("UPDATE account_fiscal_position SET zip_from = NULL WHERE zip_from = '0'")
    cr.execute("UPDATE account_fiscal_position SET zip_to = NULL WHERE zip_to = '0'")

    util.remove_field(cr, "res.partner", "contracts_count")

    util.remove_field(cr, "res.config.settings", "module_account_asset")
    util.remove_field(cr, "res.config.settings", "module_account_deferred_revenue")
    util.remove_field(cr, "res.config.settings", "module_account_reports_followup")

    util.create_column(cr, "tax_adjustments_wizard", "adjustment_type", "varchar")
    util.create_column(cr, "tax_adjustments_wizard", "tax_report_line_id", "int4")
    util.create_column(cr, "tax_adjustments_wizard", "country_id", "int4")
    util.remove_field(cr, "tax.adjustments.wizard", "tax_id")

    util.remove_model(cr, "account.invoice.import.wizard")
    util.remove_model(cr, "cash.box.in")

    # module can now be removed
    util.remove_module(cr, "l10n_fr_certification")
