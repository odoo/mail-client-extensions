from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr,
        "stock_barcode_picking_batch.picking_view_kanban_inherit_barcode_picking_batch",
        "stock_barcode_picking_batch.stock_picking_view_kanban",
    )
    util.remove_view(cr, "stock_barcode_picking_batch.stock_barcode_batch_picking_type_kanban")
