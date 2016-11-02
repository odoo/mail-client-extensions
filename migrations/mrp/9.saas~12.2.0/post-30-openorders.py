# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
from collections import defaultdict


def migrate(cr, version):
    env = util.env(cr)
    mo_obj = env['mrp.production']
    mos = mo_obj.search([('state', 'not in', ['done', 'cancel'])])
    
    #Put Unit Factor
    for mo in mos:
        cr.execute("""
            SELECT product_id, product_qty, product_uom FROM mrp_production_product_line WHERE production_id = %s ORDER BY id  
        """, (mo.id,))
        res = cr.dictfetchall()
        for move in mo.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel')):
            # Normally the first should be the correct one as they should have the same order
            ind = 0
            for line in res:
                if line['product_id'] == move.product_id.id and line['product_uom'] == move.product_uom.id:
                    # BoM line link only on top level
                    filtered_bom_lines = mo.bom_id.bom_line_ids.filtered(lambda x: x.product_id.id == line['product_id'] and x.product_uom_id.id == line['product_uom'])
                    if filtered_bom_lines: #might do an improvement when len > 1 and already chosen...
                        move.bom_line_id = filtered_bom_lines[0].id
                    move.unit_factor = line['product_qty'] / mo.product_qty
                    res.pop(ind)
                    break
                ind += 1
    
    # Need to put correct time on workorders
    cr.execute("""
        UPDATE mrp_workorder SET duration_expected = hour * 60
    """)
    
    # Need to put correct quantity on operations: time_cycle_manual
    cr.execute("""
        UPDATE mrp_routing_workcenter SET time_cycle_manual = hour_nbr * 60 + cycle_nbr * wc.time_cycle * 60 FROM mrp_workcenter wc WHERE wc.id = workcenter_id 
    """)
    
    #adapt states that might come from mrp_operation module
    cr.execute("""UPDATE mrp_workorder SET state='pending' WHERE state in ('draft', 'pause')""")
    cr.execute("""UPDATE mrp_workorder SET state='ready' WHERE state='startworking'""")
    
    # We suppose the last work order is still open (if not, you can still alter the quantities on the manufacturing order)
    # Search mos with work orders
    for mo in mos.filtered(lambda x: x.workorder_ids):
        previous_wo = False
        first_wo = True
        if mo.product_id.tracking == 'serial':
            qty_producing = 1.0
        else:
            qty_producing = mo.product_qty - mo.qty_produced
        mo.workorder_ids.filtered(lambda x: x.state not in ('done', 'cancel')).write({'qty_producing': qty_producing, 'qty_produced': mo.qty_produced})
        mo.workorder_ids.filtered(lambda x: x.state == 'done').write({'qty_producing': 0.0, 'qty_produced': mo.product_qty})
        for wo in mo.workorder_ids:
            if previous_wo:
                previous_wo.next_work_order_id = wo.id
            if wo.state != 'done' and first_wo:
                first_wo = False
                wo.state='ready'
            previous_wo = wo #still to test and put first available wo as ready
        mo.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel')).write({'workorder_id': mo.workorder_ids[-1].id})
        mo.workorder_ids[-1]._generate_lot_ids()
        
    # Create stock.move.lots
    for mo in mos:
        mo.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel')).check_move_lots()