# -*- coding: utf-8 -*-
from odoo.upgrade import util

eb = util.expand_braces


def migrate(cr, version):
    util.rename_field(cr, "sale.order", *eb("tax_totals{_json,}"))

    util.create_column(cr, "account_move_line", "is_downpayment", "boolean")
    query = """
        UPDATE account_move_line aml
           SET is_downpayment = TRUE
          FROM sale_order_line_invoice_rel r
          JOIN sale_order_line sol ON sol.id = r.order_line_id
         WHERE aml.id = r.invoice_line_id
           AND sol.is_downpayment
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_move_line", alias="aml"))
