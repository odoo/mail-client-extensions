from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "stock_barcode.stock_picking_kanban")
    util.rename_xmlid(
        cr, "stock_barcode.picking_view_kanban_inherit_barcode", "stock_barcode.stock_picking_view_kanban"
    )
