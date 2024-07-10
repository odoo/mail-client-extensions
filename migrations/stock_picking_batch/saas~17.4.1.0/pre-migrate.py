from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "stock_picking_batch.vpicktree_inherit_stock_picking_batch", "stock_picking_batch.vpicktree")
