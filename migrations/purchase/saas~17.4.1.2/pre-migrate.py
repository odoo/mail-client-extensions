from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "purchase.order.line", "taxes_id", "tax_ids")
    util.rename_field(cr, "purchase.order.line", "invoice_lines", "account_move_line_ids")
    util.rename_field(cr, "purchase.order", "invoice_ids", "account_move_ids")
