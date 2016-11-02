# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    env = util.env(cr)
    wh_obj = env['stock.warehouse'].with_context(active_test=False)
    # Add picking type for manufacturing on every warehouse
    whs = wh_obj.search([])
    whs._create_manufacturing_picking_type()
    
    # Give existing manufacturing orders / procurement rules the picking type corresponding to their location
    mo_obj = env['mrp.production']
    proc_obj = env['procurement.rule']
    # Need to do this in post as we need manufacturing picking type
    for wh in wh_obj.search([]):
        mos = mo_obj.search(['|', ('location_src_id', 'child_of', wh.view_location_id.id), ('location_dest_id', 'child_of', wh.view_location_id.id)])
        mos.write({'picking_type_id': wh.manu_type_id.id})
        proc_rules = proc_obj.search([('action', '=', 'manufacture'), 
                                      '|', ('location_id', 'child_of', wh.view_location_id.id), ('location_src_id', 'child_of', wh.view_location_id.id)])
        proc_rules.write({'picking_type_id': wh.manu_type_id.id})
    # If there are still mos without picking type, we should give it the first one
    mos = mo_obj.search([('picking_type_id', '=', False)])
    if mos:
        mos.write({'picking_type_id': wh_obj.search([], limit=1).manu_type_id.id})
    # If there are still manufacturing procurement rules without picking type, we should give it the first one
    proc_rules = proc_obj.search([('action', '=', 'manufacture'), ('picking_type_id', '=', False)])
    if proc_rules:
        proc_rules.write({'picking_type_id': wh_obj.search([], limit=1).manu_type_id.id})

    # Adapt existing states:
    # old states: draft, cancel, confirmed, ready, in_production, done
    # new states: confirmed, cancel, planned, progress, done
    # Confirm all production orders that are in draft state
    cr.execute("""SELECT id FROM mrp_production WHERE state='draft' """)
    res = cr.fetchall()
    if res:
        draft_mos = mo_obj.browse([x[0] for x in res])
        draft_mos._generate_moves()
        cr.execute("""UPDATE mrp_production SET state='confirmed' WHERE state='draft'""")
    # Confirmed, Ready -> confirmed
    cr.execute("""UPDATE mrp_production SET state='confirmed' WHERE state = 'ready'""")
    # in_production -> progress
    cr.execute("""UPDATE mrp_production SET state='progress' WHERE state = 'in_production'""")
    mos_planned = mo_obj.search([('workorder_ids', '!=', []), ('state', 'not in', ('done', 'cancel'))])
    mos_planned.write({'state': 'planned'})