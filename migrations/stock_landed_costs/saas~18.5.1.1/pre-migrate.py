from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "stock.landed.cost", "stock_valuation_layer_ids")
