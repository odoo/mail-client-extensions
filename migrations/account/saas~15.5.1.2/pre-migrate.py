# -*- coding: utf-8 -*-
from odoo.osv.expression import get_unaccent_wrapper
from odoo.tools import html_escape

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
    unaccent = get_unaccent_wrapper(cr)
    cr.execute(
        r"""
        UPDATE account_account
           SET code = BTRIM(
               REGEXP_REPLACE(
                   REGEXP_REPLACE(
                       REGEXP_REPLACE({code}, '[,|; \-_/\~٬]', '.', 'g'),
                       '[^A-Za-z0-9.]', '', 'g'),
                   '[.]+', '.', 'g'),
               '.')
         WHERE code !~ '^[A-Za-z0-9.]+$'
         RETURNING name, code;
    """.format(
            code=unaccent("code"),
        )
    )

    if cr.rowcount:
        message = """
        <details>
        <summary>
            The following accounts were using invalid account codes which were modified during the migration.
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
    cr.execute(
        """
        UPDATE account_payment_term_line
           SET months = 0,
               days = 0,
               end_month = True,
               days_after = days
         WHERE option IN ('day_current_month', 'after_invoice_month');

        UPDATE account_payment_term_line
           SET months = 0,
               days = days,
               end_month = (days_after != 0),
               days_after = CASE WHEN days_after >= 30 THEN 0 ELSE days_after END
         WHERE option = 'day_after_invoice_date';

        UPDATE account_payment_term_line
           SET months = (days >= 30)::int,
               days = 0,
               end_month = True,
               days_after = CASE WHEN days < 30 THEN days ELSE 0 END
         WHERE option = 'day_following_month';
        """
    )
    util.remove_field(cr, "account.payment.term.line", "option")
    util.remove_field(cr, "account.payment.term.line", "sequence")
