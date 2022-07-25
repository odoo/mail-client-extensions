# -*- coding: utf-8 -*-
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
