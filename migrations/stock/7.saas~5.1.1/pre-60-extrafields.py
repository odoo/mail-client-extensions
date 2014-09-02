from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    """
    Create fields at forehand
    """
    
    util.create_column(cr, 'product_template', 'track_incoming', 'boolean')
    util.create_column(cr, 'product_template', 'track_outgoing', 'boolean')
    cr.execute("""
        UPDATE product_template SET track_incoming = pp.track_incoming, track_outgoing = pp.track_outgoing
        FROM product_product pp WHERE product_template.id = pp.product_tmpl_id 
    """)
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
    util.create_column(cr, 'stock_warehouse', 'code', 'char(5)')
    util.create_column(cr, 'stock_warehouse', 'reception_steps', 'char')
    util.create_column(cr, 'stock_warehouse', 'delivery_steps', 'char')
    util.create_column(cr, 'stock_warehouse', 'view_location_id', 'int4')
    util.create_column(cr, 'stock_warehouse', 'wh_input_stock_loc_id', 'int4')
    util.create_column(cr, 'stock_warehouse', 'wh_qc_stock_loc_id', 'int4')
    util.create_column(cr, 'stock_warehouse', 'wh_output_stock_loc_id', 'int4')
    util.create_column(cr, 'stock_warehouse', 'wh_pack_stock_loc_id', 'int4')
    util.create_column(cr, 'stock_warehouse', 'default_resupply_wh_id', 'int4')
