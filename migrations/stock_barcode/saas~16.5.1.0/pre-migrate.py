from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "stock.move.line", "is_completed")
    util.remove_view(cr, "stock_barcode.view_picking_type_form_inherit_stock_barcode")
