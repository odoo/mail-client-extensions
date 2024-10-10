from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "purchase_order_line", "state")
    util.remove_column(cr, "purchase_order_line", "currency_id")
