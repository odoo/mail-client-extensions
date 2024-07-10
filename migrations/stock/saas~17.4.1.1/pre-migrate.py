from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "stock.picking", "weight_bulk", "stock_delivery", "stock")
    util.move_field_to_module(cr, "stock.picking", "shipping_weight", "stock_delivery", "stock")
    util.move_field_to_module(cr, "stock.quant.package", "shipping_weight", "stock_delivery", "stock")
