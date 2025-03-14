from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "stock_picking_batch.view_picking_tree_batch")
    util.remove_field(cr, "stock.picking.batch", "show_validate")
