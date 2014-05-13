from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    """
        1 Procurement method moved from procurements to stock moves
        2 Change states from procurements
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
    
    # Change states of procurements: 
    # draft, ready should be confirmed 
    # waiting should pass to running 
    cr.execute("""
    UPDATE procurement_order po
    SET state = 'confirmed'
    WHERE po.state in ('draft', 'ready')
    """)
    cr.execute("""
    UPDATE procurement_order po
    SET state = 'running'
    WHERE po.state = 'waiting'
    """)