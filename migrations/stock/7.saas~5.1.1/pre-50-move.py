from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_field(cr, 'stock_move', 'product_qty', 'product_uom_qty')
    util.rename_field(cr, 'stock_move', 'prodlot_id', 'restrict_lot_id')