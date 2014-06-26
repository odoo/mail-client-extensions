from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    """
        As product_qty will become a function field, the old value should be in product_uom_qty
        The lots of a stock move can still be used with restrict_lot_id
    """
    util.rename_field(cr, 'stock.move', 'product_qty', 'product_uom_qty')
    util.rename_field(cr, 'stock.move', 'prodlot_id', 'restrict_lot_id')
    
    # For inventories, we need to change the many2many to many2one for correcting the moves
    util.rename_field(cr, 'stock.inventory.line', 'product_uom', 'product_uom_id')
    util.create_column(cr, 'stock_move', 'inventory_id', 'int4')
    cr.execute("""
        UPDATE stock_move 
        SET inventory_id = inv.id
        FROM stock_inventory inv, stock_inventory_move_rel invmove
        WHERE invmove.move_id = stock_move.id AND invmove.inventory_id = inv.id
    """)
    
    
    