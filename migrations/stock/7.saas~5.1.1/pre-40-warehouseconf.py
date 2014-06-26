from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    """
        In order to know whether a warehouse is one or two-step input/output, 
        we check if the input / output location of the warehouse were different than stock
        and if they were chained.  If not chained it can stay as location
    """
    util.rename_field(cr, 'stock.warehouse', 'lot_input_id', 'wh_input_stock_loc_id')
    util.rename_field(cr, 'stock.warehouse', 'lot_output_id', 'wh_output_stock_loc_id')
    cr.execute("""ALTER TABLE stock_warehouse ALTER COLUMN wh_input_stock_loc_id DROP NOT NULL""")
    cr.execute("""ALTER TABLE stock_warehouse ALTER COLUMN wh_output_stock_loc_id DROP NOT NULL""")
    cr.execute("""UPDATE stock_warehouse SET wh_input_stock_loc_id = NULL 
                FROM stock_location  
                WHERE (stock_warehouse.wh_input_stock_loc_id = stock_location.id AND
                stock_location.chained_auto_packing != 'manual') OR wh_input_stock_loc_id = lot_stock_id""")
     
    cr.execute("""UPDATE stock_warehouse SET wh_output_stock_loc_id = NULL 
                FROM stock_location  
                WHERE (stock_warehouse.wh_output_stock_loc_id = stock_location.id AND
                stock_location.chained_auto_packing != 'manual') OR wh_output_stock_loc_id = lot_stock_id""")


    # Create route for all pull push rules
    #cr.execute("""INSERT INTO stock_location_route 
    #""")
    # Migration of stock_location module
    util.rename_field(cr, 'stock.location.path', 'picking_type', '_picking_type')
    util.rename_field(cr, 'stock.location.path', 'product_id', '_product_id')
    util.rename_field(cr, 'stock.move', 'cancel_cascade', 'propagate')
    
    