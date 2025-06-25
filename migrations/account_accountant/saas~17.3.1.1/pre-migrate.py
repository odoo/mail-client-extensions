from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "bank.rec.widget", "st_line_narration")

    # Deferred
    util.create_column(cr, "account_move_line", "deferred_start_date", "date")  # for new install
    for deferred_type in ("expense", "revenue"):
        method_col = f"deferred_{deferred_type}_amount_computation_method"
        util.create_column(cr, "res_company", method_col, "varchar")
        journal_col = f"deferred_{deferred_type}_journal_id"
        util.create_column(cr, "res_company", journal_col, "int4")
        if not util.column_exists(cr, "res_company", "deferred_journal_id"):
            continue
        query = util.format_query(
            cr,
            """
            UPDATE res_company
               SET {} = deferred_amount_computation_method,
                   {} = deferred_journal_id
            """,
            method_col,
            journal_col,
        )
        cr.execute(query)
    util.remove_field(cr, "res.company", "deferred_amount_computation_method")
    util.remove_field(cr, "res.company", "deferred_journal_id")
    util.remove_field(cr, "res.config.settings", "deferred_amount_computation_method")
    util.remove_field(cr, "res.config.settings", "deferred_journal_id")

    util.move_field_to_module(cr, "account.move.line", "expected_pay_date", "account_reports", "account_accountant")
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("{account_accountant,accountant}.menu_accounting"))
