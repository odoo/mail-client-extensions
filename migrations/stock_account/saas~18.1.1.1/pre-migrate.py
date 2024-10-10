from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "stock_valuation_layer", "categ_id")
