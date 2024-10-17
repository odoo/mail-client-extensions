from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "stock.move.line", "product_packaging_id")
    util.remove_field(cr, "stock.move.line", "product_packaging_uom_qty")
