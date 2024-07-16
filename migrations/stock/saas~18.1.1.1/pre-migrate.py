from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "stock_lot", "product_uom_id")
    util.remove_column(cr, "stock_move_line", "reference")
    util.remove_column(cr, "stock_warehouse_orderpoint", "product_category_id")
    util.remove_column(cr, "stock_quant", "storage_category_id")
    util.remove_field(cr, "stock.package.destination", "picking_id")
