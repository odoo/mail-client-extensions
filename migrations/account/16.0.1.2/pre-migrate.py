# -*- coding: utf-8 -*-
from xmlrpc.client import MAXINT, MININT

from odoo.osv.expression import get_unaccent_wrapper
from odoo.tools import html_escape

from odoo.addons.base.maintenance.migrations.util.accounting import upgrade_analytic_distribution
from odoo.upgrade import util

eb = util.expand_braces


def migrate(cr, version):
    util.remove_view(cr, "account.view_move_line_tree_grouped")
    util.remove_view(cr, "account.view_account_move_line_filter_with_root_selection")
    util.remove_record(cr, "account.action_account_moves_ledger_general")

    query = """
        UPDATE account_move_line line
           SET display_type = CASE
                   WHEN move.move_type = 'entry' THEN 'product'
                   WHEN line.tax_line_id IS NOT NULL THEN 'tax'
                   WHEN line.is_rounding_line THEN 'rounding'
                   WHEN account.account_type IN ('asset_receivable', 'liability_payable') THEN 'payment_term'
                   ELSE 'product'
               END
          FROM account_move move,
               account_account account
         WHERE line.move_id = move.id
           AND line.account_id = account.id
           AND line.display_type IS NULL
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_move_line", alias="line"))

    util.remove_field(cr, "account.move.line", "is_rounding_line")
    util.remove_field(cr, "account.move.line", "exclude_from_invoice_tab")
    util.remove_field(cr, "account.move.line", "recompute_tax_line")
    util.rename_field(cr, "account.move", *eb("tax_totals{_json,}"))

    # Reportalypse
    cr.execute("CREATE TABLE account_tax_report_line_tags_rel_backup AS TABLE account_tax_report_line_tags_rel")
    cr.execute(
        "ALTER TABLE account_tax_report_line_tags_rel_backup ADD PRIMARY KEY(account_tax_report_line_id, account_account_tag_id)"
    )

    for model in ("account.tax.carryover.line", "account.tax.report.line", "account.tax.report"):
        util.remove_model(cr, model, drop_table=False)

    for model in ("tax.adjustments.wizard", "account.common.journal.report", "account.print.journal"):
        util.remove_model(cr, model)

    util.remove_field(cr, "account_reports.export.wizard", "report_model")
    util.remove_field(cr, "account.tax.repartition.line.template", "plus_report_line_ids")
    util.remove_field(cr, "account.tax.repartition.line.template", "minus_report_line_ids")
    util.remove_field(cr, "account.account.tag", "tax_report_line_ids")
    util.remove_field(cr, "res.config.settings", "module_l10n_fr_fec_import")

    # With reportalypse, account_accounts should all respect the regex ^[A-Za-z0-9.]+$.
    # This aim to handle the existing accounts that could be "wrong", by:
    #     - Running unaccent on them if possible, depending on weither it is available or not.
    #     - Replacing all characters usually used as separator by dots.
    #     - Removing every other special characters.
    #     - Making sure we don't have multiple dots at once. (Using [.]+ as using {2,} wouldn't work with format.
    #     - Finally removing trailing dots that could have been there by result of the transformation.

    # Catch possible duplicates before the replacement and update them to avoid constraint errors.
    unaccent = get_unaccent_wrapper(cr)
    cr.execute(
        r"""WITH data AS (
                SELECT id,
                       company_id,
                       code,
                       BTRIM(
                        REGEXP_REPLACE(
                            REGEXP_REPLACE(
                                REGEXP_REPLACE({code}, '[,|; \-_/\~٬]', '.', 'g'),
                                '[^A-Za-z0-9.]', '', 'g'),
                            '[.]+', '.', 'g'),
                        '.') as new_code
                  FROM account_account
            ),
            replacement AS (
                SELECT array_agg(id ORDER BY code=new_code desc, id) ids,
                       new_code
                  FROM data
                 WHERE new_code != code
              GROUP BY company_id, new_code
            )
               UPDATE account_account
                  SET code = r.new_code ||
                             CASE
                                WHEN array_position(r.ids, id) > 1 THEN '.dup' || array_position(r.ids, id) - 1
                                ELSE ''
                             END
                 FROM replacement r
                WHERE id = ANY(r.ids)
            RETURNING name, code
         """.format(
            code=unaccent("code")
        )
    )

    if cr.rowcount:
        message = """
        <details>
        <summary>
            The following accounts were using invalid account codes which were modified during the migration.
            If there were duplicated codes after cleanup they will have `.dupN` suffix.
            Please review the changes and correct them if needed.
            The account codes should now only contain alphanumeric characters and dots.
        </summary>
        <ul>
            {}
        </ul>
        </details>
        """.format(
            "\n".join(
                f"<li>'{html_escape(name)}' had its code changed to: '{html_escape(code)}' "
                for name, code in cr.fetchall()
            )
        )
        util.add_to_migration_reports(category="Accounting", format="html", message=message)

    # Refactoring of payment terms
    util.remove_view(cr, "account.view_payment_term_line_form")
    util.remove_view(cr, "account.view_payment_term_line_tree")
    util.rename_field(cr, "account.payment.term.line", "day_of_the_month", "days_after")
    util.create_column(cr, "account_payment_term_line", "months", "integer", default=0)
    util.create_column(cr, "account_payment_term_line", "end_month", "boolean", default=False)
    util.parallel_execute(
        cr,
        [
            """
            UPDATE account_payment_term_line
               SET months = 0,
                   days = 0,
                   end_month = True,
                   days_after = days
             WHERE option IN ('day_current_month', 'after_invoice_month');
            """,
            """
            UPDATE account_payment_term_line
               SET months = 0,
                   days = days,
                   end_month = (days_after != 0),
                   days_after = CASE WHEN days_after >= 30 THEN 0 ELSE days_after END
             WHERE option = 'day_after_invoice_date';
            """,
            """
            UPDATE account_payment_term_line
               SET months = (days >= 30)::int,
                   days = 0,
                   end_month = True,
                   days_after = CASE WHEN days < 30 THEN days ELSE 0 END
             WHERE option = 'day_following_month';
            """,
        ],
    )
    util.remove_field(cr, "account.payment.term.line", "option")
    util.remove_field(cr, "account.payment.term.line", "sequence")

    # Remove unused view
    util.remove_record(cr, "account.action_account_chart_template_form")
    util.remove_view(cr, "account.view_account_chart_template_form")
    util.remove_view(cr, "account.view_account_chart_template_seacrh")
    util.remove_view(cr, "account.view_account_chart_template_tree")
    util.remove_view(cr, "account.view_account_template_form")
    util.remove_view(cr, "account.view_account_template_tree")
    util.remove_view(cr, "account.view_account_template_search")
    util.remove_view(cr, "account.account_common_report_view")
    util.remove_model(cr, "account.common.report")

    cr.execute(
        """
        ALTER TABLE res_company
        RENAME COLUMN account_onboarding_create_invoice_state
        TO account_onboarding_create_invoice_state_flag
    """
    )
    cr.execute(
        """
        ALTER TABLE res_company
        ALTER COLUMN account_onboarding_create_invoice_state_flag
        TYPE boolean
        USING account_onboarding_create_invoice_state_flag
        IN ('done', 'just_done')
    """
    )
    # Move attachment_ids from account_accountant to account, for use in l10n_mx_edi
    util.move_field_to_module(cr, "account.move", "attachment_ids", "account_accountant", "account")

    # Analytic
    upgrade_analytic_distribution(cr, model="account.move.line")
    upgrade_analytic_distribution(
        cr,
        model="account.reconcile.model.line",
        tag_table="account_reconcile_model_analytic_tag_rel",
    )

    util.rename_field(cr, "account.analytic.line", "move_id", "move_line_id")  # was never a move
    util.create_column(cr, "account_analytic_line", "journal_id", "int4")
    query = """
        UPDATE account_analytic_line line
           SET journal_id = aml.journal_id,
               partner_id = COALESCE(aml.partner_id, line.partner_id)
          FROM account_move_line aml
         WHERE line.move_line_id = aml.id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_analytic_line", alias="line"))

    util.remove_model(cr, "account.analytic.default")
    util.remove_field(cr, "account.invoice.report", "analytic_account_id")
    util.remove_field(cr, "res.config.settings", "group_analytic_tags")
    util.remove_record(cr, "account.analytic_default_comp_rule")
    util.remove_view(cr, "account.view_account_invoice_report_search_analytic_accounting")
    util.remove_view(cr, "account.account_analytic_account_view_form_inherit")

    util.remove_model(cr, "account.cashbox.line")
    util.remove_model(cr, "cash.box.out")
    util.remove_model(cr, "account.bank.statement.cashbox")
    util.remove_model(cr, "account.bank.statement.closebalance")

    util.remove_view(cr, "account.view_bank_statement_form")
    util.remove_view(cr, "account.view_bank_statement_line_search")
    util.remove_view(cr, "account.view_bank_statement_line_form")
    util.remove_view(cr, "account.view_bank_statement_line_tree")

    util.rename_field(cr, "account.payment", "reconciled_statements_count", "reconciled_statement_lines_count")
    util.remove_field(cr, "account.payment", "reconciled_statement_ids")

    util.remove_field(cr, "account.move", "statement_id", skip_inherit=("account.bank.statement.line",))

    util.remove_inherit_from_model(cr, "account.bank.statement", "mail.thread")
    util.remove_inherit_from_model(cr, "account.bank.statement", "sequence.mixin")
    for field in (
        "date_done",
        "state",
        "total_entry_encoding",
        "difference",
        "is_difference_zero",
        "cashbox_end_id",
        "cashbox_start_id",
        "user_id",
        "previous_statement_id",
        "is_valid_balance_start",
        "all_lines_reconciled",
        "move_line_count",
        "move_line_ids",
        "journal_type",
        "country_code",
    ):
        util.remove_field(cr, "account.bank.statement", field)

    util.create_column(cr, "account_bank_statement_line", "internal_index", "varchar")
    util.create_column(cr, "account_bank_statement_line", "currency_id", "int4")

    query = cr.mogrify(
        """
            UPDATE account_bank_statement_line
               SET internal_index = REPLACE(account_move.date::text, '-', '')
                                    || TO_CHAR(%s::int8 - COALESCE(account_bank_statement_line.sequence, %s), 'fm0000000000')
                                    || TO_CHAR(account_bank_statement_line.id, 'fm0000000000'),
                   currency_id = COALESCE(account_journal.currency_id, res_company.currency_id)
              FROM account_move
              JOIN account_journal
                ON account_journal.id = account_move.journal_id
              JOIN res_company
                ON res_company.id = account_move.company_id
             WHERE account_move.statement_line_id = account_bank_statement_line.id
        """,
        [MAXINT, MININT],
    ).decode()

    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_bank_statement_line"))

    cr.execute(
        "CREATE INDEX account_bank_statement_line_internal_index_index ON account_bank_statement_line(internal_index)"
    )

    util.create_column(cr, "account_bank_statement", "first_line_index", "varchar")
    util.remove_column(cr, "account_bank_statement", "date")
    util.create_column(cr, "account_bank_statement", "date", "date")

    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
        WITH min_max_statement_index AS (
            SELECT st_line.statement_id,
                   MIN(st_line.internal_index) AS min_internal_index,
                   MAX(st_line.internal_index) AS max_internal_index
              FROM account_bank_statement_line st_line
              JOIN account_bank_statement b
                ON b.id = st_line.statement_id
             WHERE st_line.statement_id IS NOT NULL
               AND {parallel_filter}
          GROUP BY st_line.statement_id
        )
        UPDATE account_bank_statement
           SET first_line_index = min_max_statement_index.min_internal_index,
               date = move.date
          FROM min_max_statement_index
          JOIN account_bank_statement_line st_line
            ON st_line.internal_index = min_max_statement_index.max_internal_index
          JOIN account_move move
            ON move.statement_line_id = st_line.id
         WHERE account_bank_statement.id = min_max_statement_index.statement_id
        """,
            table="account_bank_statement",
            alias="b",
        ),
    )

    util.create_column(cr, "account_bank_statement", "is_complete", "bool")
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
        WITH st_line_amount_per_st AS (
            SELECT st_line.statement_id,
                   COALESCE(journal.currency_id, company.currency_id) AS currency_id,
                   SUM(st_line.amount) AS amount
              FROM account_bank_statement_line st_line
              JOIN account_bank_statement b
                ON b.id = st_line.statement_id
              JOIN account_move move
                ON move.statement_line_id = st_line.id
              JOIN account_journal journal
                ON journal.id = move.journal_id
              JOIN res_company company
                ON company.id = journal.company_id
             WHERE {parallel_filter}
          GROUP BY st_line.statement_id, journal.currency_id, company.currency_id
        )
        UPDATE account_bank_statement
           SET is_complete = ROUND(
                    account_bank_statement.balance_end_real - st_line_amount_per_st.amount - account_bank_statement.balance_start,
                    res_currency.decimal_places
                ) = 0
          FROM st_line_amount_per_st
          JOIN res_currency
            ON res_currency.id = st_line_amount_per_st.currency_id
         WHERE st_line_amount_per_st.statement_id = account_bank_statement.id
        """,
            table="account_bank_statement",
            alias="b",
        ),
    )
