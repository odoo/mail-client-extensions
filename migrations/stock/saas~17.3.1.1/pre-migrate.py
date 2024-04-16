from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "stock_move_line", "product_category_name")
