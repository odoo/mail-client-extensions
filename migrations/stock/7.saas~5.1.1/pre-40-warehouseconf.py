from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    #We should change warehouse config to check one-step/two-step input/output
    util.rename_field(cr, 'stock_warehouse', 'lot_input_id', 'wh_input_stock_loc_id')
    util.rename_field(cr, 'stock_warehouse', 'lot_output_id', 'wh_output_stock_loc_id')
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
