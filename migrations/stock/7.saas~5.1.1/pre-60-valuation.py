from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    """
    Valuation field should be renamed in order to be reused later on
    """
    util.rename_field(cr, 'product_product', 'valuation', '_valuation_mig')
    
    
    cr.execute("update ir_model_data set module='stock_account' where name='group_stock_inventory_valuation'")


    # Create columns already for warehouse
    util.create_column(cr, 'stock_warehouse', 'mto_pull_id', 'int4')
    util.create_column(cr, 'stock_warehouse', 'pick_type_id', 'int4')
    util.create_column(cr, 'stock_warehouse', 'pack_type_id', 'int4')
    util.create_column(cr, 'stock_warehouse', 'out_type_id', 'int4')
    util.create_column(cr, 'stock_warehouse', 'in_type_id', 'int4')
    util.create_column(cr, 'stock_warehouse', 'int_type_id', 'int4')
    util.create_column(cr, 'stock_warehouse', 'crossdock_route_id', 'int4')
    util.create_column(cr, 'stock_warehouse', 'reception_route_id', 'int4')
    util.create_column(cr, 'stock_warehouse', 'delivery_route_id', 'int4')
    util.create_column(cr, 'stock_warehouse', 'resupply_from_wh', 'boolean')
    util.create_column(cr, 'stock_warehouse', 'code', 'char')
    util.create_column(cr, 'stock_warehouse', 'reception_steps', 'char')
    util.create_column(cr, 'stock_warehouse', 'delivery_steps', 'char')
    util.create_column(cr, 'stock_warehouse', 'view_location_id', 'int4')
    util.create_column(cr, 'stock_warehouse', 'wh_input_stock_loc_id', 'int4')
    util.create_column(cr, 'stock_warehouse', 'wh_qc_stock_loc_id', 'int4')
    util.create_column(cr, 'stock_warehouse', 'wh_output_stock_loc_id', 'int4')
    util.create_column(cr, 'stock_warehouse', 'wh_pack_stock_loc_id', 'int4')
    util.create_column(cr, 'stock_warehouse', 'default_resupply_wh_id', 'int4')
