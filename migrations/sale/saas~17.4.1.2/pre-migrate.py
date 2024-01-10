from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "website_sale"):
        util.move_field_to_module(cr, "sale.order.line", "linked_line_id", "website_sale", "sale")
        util.move_field_to_module(cr, "sale.order.line", "option_line_ids", "website_sale", "sale")
        util.rename_field(cr, "sale.order.line", "option_line_ids", "linked_line_ids")
    util.remove_field(cr, "sale.advance.payment.inv", "deduct_down_payments")
    util.rename_field(cr, "sale.advance.payment.inv", "sale_order_ids", "order_ids")
    util.rename_field(cr, "sale.order.line", "tax_id", "tax_ids")
    util.rename_field(cr, "sale.order.line", "invoice_lines", "account_move_line_ids")
    util.rename_field(cr, "sale.order", "invoice_ids", "account_move_ids")
