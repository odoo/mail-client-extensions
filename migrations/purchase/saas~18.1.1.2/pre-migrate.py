from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "purchase_order_line", "state")
    util.remove_column(cr, "purchase_order_line", "currency_id")
    util.rename_field(cr, "purchase.order.line", "product_uom", "product_uom_id")
    util.rename_field(cr, "purchase.report", "product_uom", "product_uom_id")
