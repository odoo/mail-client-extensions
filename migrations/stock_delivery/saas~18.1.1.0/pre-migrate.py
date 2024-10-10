from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "stock_move_line", "carrier_id")
