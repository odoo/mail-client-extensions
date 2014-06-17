from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    """
        As product_qty will become a function field, the old value should be in product_uom_qty
        The lots of a stock move can still be used with 
    """
    util.rename_field(cr, 'stock_move', 'product_qty', 'product_uom_qty')
    util.rename_field(cr, 'stock_move', 'prodlot_id', 'restrict_lot_id')