# -*- coding: utf-8 -*-
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    """
        Link mto route with products that had route MTO
    """
    registry = RegistryManager.get(cr.dbname)
    mod_obj = registry['ir.model.data']
    mto_route = mod_obj.xmlid_to_res_id(cr, SUPERUSER_ID, 'stock.route_warehouse0_mto')
    cr.execute("""
    INSERT INTO stock_route_product (product_id, route_id)
    select id, %s from product_template where procure_method = 'make_to_order' 
    """, (mto_route,))


    if util.column_exists(cr, 'procurement_rule', '_product_id'):
        # Let's create routes per product if there are pull/push related to this product
        # Might work more efficiently if we create an in between column on the route
        templates = {}
        cr.execute("""SELECT product_tmpl_id, pt.name FROM procurement_rule pr, product_product pp, product_template pt
        WHERE pp.id = pr._product_id AND pt.id = pp.product_tmpl_id GROUP BY product_tmpl_id, pt.name""")
        prod_obj = registry['product.template']
        route_obj = registry['stock.location.route']
        for templ in cr.fetchall():
            route_id = route_obj.create(cr, SUPERUSER_ID, {'name': templ[1], 'product_selectable': False})
            prod_obj.write(cr, SUPERUSER_ID, [templ[0]], {'route_ids': [(4, route_id)]})
            templates[templ[0]] = route_id
        cr.execute("""SELECT product_tmpl_id, pt.name FROM stock_location_path pr, product_product pp, product_template pt
        WHERE pp.id = pr._product_id AND pt.id = pp.product_tmpl_id GROUP BY product_tmpl_id, pt.name""")
        for templ in cr.fetchall():
            if not templates.get(templ[0]):
                route_id = route_obj.create(cr, SUPERUSER_ID, {'name': templ[1], 'product_selectable': False})
                prod_obj.write(cr, SUPERUSER_ID, [templ[0]], {'route_ids': [(4, route_id)]})
                templates[templ[0]] = route_id
        for templ in templates.keys():
            cr.execute("""UPDATE procurement_rule SET route_id = %s FROM product_product pp 
            WHERE pp.id = procurement_rule._product_id AND pp.product_tmpl_id = %s""", (templates[templ], templ,))
            cr.execute("""UPDATE stock_location_path SET route_id = %s FROM product_product pp 
            WHERE pp.id = stock_location_path._product_id AND pp.product_tmpl_id = %s""", (templates[templ], templ,))
            
        
        # We need to put a picking_type on all 
        picking_in = mod_obj.xmlid_to_res_id(cr, SUPERUSER_ID, 'stock.picking_type_in')
        picking_out = mod_obj.xmlid_to_res_id(cr, SUPERUSER_ID, 'stock.picking_type_out')
        picking_internal = mod_obj.xmlid_to_res_id(cr, SUPERUSER_ID, 'stock.picking_type_internal')
        
        cr.execute("""
            UPDATE procurement_rule SET picking_type_id = %s where picking_type_id is null 
            and _picking_type='in'
        """, (picking_in,))
        cr.execute("""
            UPDATE procurement_rule SET picking_type_id = %s where picking_type_id is null 
            and _picking_type='out'
        """, (picking_out,))
        cr.execute("""
            UPDATE procurement_rule SET picking_type_id = %s where picking_type_id is null 
            and _picking_type='internal'
        """, (picking_internal,))
        cr.execute("""
            UPDATE stock_location_path SET picking_type_id = %s where picking_type_id is null 
            and _picking_type='in'
        """, (picking_in,))
        cr.execute("""
            UPDATE stock_location_path SET picking_type_id = %s where picking_type_id is null 
            and _picking_type='out'
        """, (picking_out,))
        cr.execute("""
            UPDATE stock_location_path SET picking_type_id = %s where picking_type_id is null 
            and _picking_type='internal'
        """, (picking_internal,))
    
    # We need to move customer locations 'not under Customers' to 'under Customers'
    # This is needed as the procurement rule is in Customers
    location_obj = registry['stock.location']
    customer_loc = mod_obj.xmlid_to_res_id(cr, SUPERUSER_ID, 'stock.stock_location_customers')
    locations = location_obj.search(cr, SUPERUSER_ID, ['&', ('location_id.usage', '!=', 'customer'), '&', ('usage', '=', 'customer'), '!', ('id', 'child_of', customer_loc)])
    location_obj.write(cr, SUPERUSER_ID, locations, {'location_id': customer_loc})
    
    cr.execute("""
        UPDATE product_template SET track_incoming = pp.track_incoming, track_outgoing = pp.track_outgoing
        FROM product_product pp WHERE product_template.id = pp.product_tmpl_id 
    """)