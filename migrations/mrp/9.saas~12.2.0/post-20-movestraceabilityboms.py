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
         WHERE p.routing_id != b.routing_id
         OR (p.routing_id is null and b.routing_id is not null) 
         OR (p.routing_id is not null and b.routing_id is null)
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