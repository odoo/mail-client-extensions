# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
from collections import defaultdict

def migrate(cr, version):
    env = util.env(cr)
    
        
    # Traceability was done before with consumed_for field on moves.  
    # Now, it is done with consumed_quant_ids / produced_quant_ids on the quants themselves
    # TODO: need to set also maybe if consumed_for was False (consume only case -> detail) 
    cr.execute("""
        INSERT INTO stock_quant_consume_rel (consume_quant_id, produce_quant_id) 
            (SELECT s1.quant_id, s2.quant_id 
            FROM stock_move move, stock_quant_move_rel s1, stock_quant_move_rel s2 
            WHERE s1.move_id = move.id AND s2.move_id = move.consumed_for 
                AND consumed_for is not null);
    """)
    
    # Create stock.move.lots (will be one for every stock move)
    cr.execute("""
        INSERT INTO stock_move_lots (create_uid, create_date, product_id, done_wo, done_move, production_id, move_id, quantity, quantity_done, lot_id) 
        SELECT create_uid, create_date, product_id, 't', 't', COALESCE(raw_material_production_id, production_id), id, product_uom_qty, product_uom_qty, restrict_lot_id 
        FROM stock_move 
        WHERE (raw_material_production_id is not null OR production_id is not null) AND
         restrict_lot_id is not null and state = 'done';
    """)
    
    # Set quantity consumed/produced for the different moves already done without lot/SN
    cr.execute("""
        UPDATE stock_move SET quantity_done_store = product_uom_qty
        WHERE (raw_material_production_id is not null OR production_id is not null)
            AND restrict_lot_id IS NULL AND state='done';
    """)


    # As the routing_id on the production order became a related with the routing on the BoM,
    # you need a different BoM for every routing_id used
    Bom = env['mrp.bom']
    Routing = env['mrp.routing']
    created_boms = defaultdict(dict)
    cr.execute("""
        SELECT p.id, b.id, p.routing_id
          FROM mrp_production p
          JOIN mrp_bom b ON b.id = p.bom_id
          JOIN mrp_routing_workcenter op ON op.routing_id = p.routing_id
         WHERE (p.routing_id != b.routing_id
         OR (p.routing_id is not null and b.routing_id is null))
         AND EXISTS(SELECT * FROM mrp_routing_workcenter WHERE routing_id = p.routing_id) 
         OR (p.routing_id is null and b.routing_id is not null)
    """)
    for pid, bid, rid in cr.fetchall():
        new_bid = created_boms[bid].get(rid)
        if not new_bid:
            #route = Routing.browse(rid).display_name
            bom = Bom.browse(bid)
            #name = '%s (Via %s)' % (bom.product_tmpl_id.name, route) -> no name field on bom
            new_bid = bom.copy({'routing_id': rid}).id
            created_boms[bid][rid] = new_bid
        # in sql to avoid all fields recomputation
        cr.execute("UPDATE mrp_production SET bom_id=%s WHERE id=%s", [new_bid, pid])

    # Work orders should be done if the related production order is done
    cr.execute("""
        UPDATE mrp_workorder w SET state='done' FROM mrp_production p 
          WHERE p.id = w.production_id AND p.state='done';
    """)
    # And cancel when related production order is cancelled
    cr.execute("""
        UPDATE mrp_workorder w SET state='cancel' FROM mrp_production p 
          WHERE p.id = w.production_id AND p.state='cancel';
    """)
    
    cr.execute("""SELECT p.location_src_id, r.location_id
                FROM mrp_routing r, mrp_production p 
                WHERE r.location_id is not null AND p.routing_id = r.id  
                AND p.location_src_id != r.location_id GROUP BY r.location_id, p.location_src_id""")
    res = cr.fetchall()
    if res and res[0]:
        #Search all routings with a special location and generate routes for it
        route = env['stock.location.route'].create({'name': "Pickings Before Manufacturing", 
                                                        'product_selectable': False,
                                                        'product_categ_selectable': True})
        product_categories = env['product.category'].search([('parent_id', '=', False)])
        product_categories.write({'route_ids': [(4, route.id)]})
    picking_type_int = env['stock.picking.type'].search([('code', '=', 'internal')], limit=1)
    for source_location_id, location_id in res:
        # Customer location
        prod_loc = env.ref('stock.location_production')
        location_name = env['stock.location'].browse(location_id).display_name
        location_source_name = env['stock.location'].browse(source_location_id).display_name
        env['procurement.rule'].create({'name': 'Make to Order %s to Production ' % (location_name,), 
                                        'location_id': prod_loc.id, 
                                        'location_src_id': location_id,
                                        'procure_method': 'make_to_order', 
                                        'route_id': route.id, 
                                        'action': 'move',
                                        'picking_type_id': picking_type_int.id, })
        env['procurement.rule'].create({'name': 'Before manufacturing from %s to %s' % (location_source_name, location_name), 
                                        'location_id': location_id, 
                                        'location_src_id': source_location_id, 
                                        'route_id': route.id, 
                                        'action': 'move', 
                                        'picking_type_id': picking_type_int.id})
    #Remove routing_id on production_orders where the routing does not have any operations 
    cr.execute("""
        UPDATE mrp_production p SET routing_id = NULL 
            WHERE routing_id is NOT NULL AND p.state NOT IN ('done', 'cancel') AND
            NOT EXISTS (SELECT id FROM mrp_routing_workcenter w WHERE w.routing_id = p.routing_id)
    """)