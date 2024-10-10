from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "stock_warehouse_orderpoint", "vendor_id")
