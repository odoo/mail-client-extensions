from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    """
        Procurement method moved from procurements to stock moves
        
    """
    util.create_column(cr, 'stock_move', 'procure_method', 'varchar')
    
    cr.execute("""
    UPDATE stock_move move
    SET procure_method = p.procure_method
    FROM procurement_order p WHERE p.move_id = move.id
    """)
    cr.execute("""delete from procurement_order where procure_method='make_to_stock'""")
    
    #Rename column move_dest_id
    util.rename_field(cr, 'procurement_order', 'move_id', 'move_dest_id')