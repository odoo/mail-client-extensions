from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "purchase_order_line", "sale_order_id")
