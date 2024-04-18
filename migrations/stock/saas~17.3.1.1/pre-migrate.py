from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "stock_move_line", "product_category_name")
    util.remove_column(cr, "stock_warehouse_orderpoint", "qty_to_order")
