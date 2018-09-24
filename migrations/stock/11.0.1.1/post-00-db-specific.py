# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def _db_epictv(cr, version):
    moves = util.env(cr)['stock.move'].search([
        ('state','in', ('assigned','partially_available')),
        ('move_line_ids','=', False)])
    moves.write({'state':'confirmed' })
    moves._action_assign()

    dom = [('picking_id','=', False), ('state', '=', 'done')]
    for move_line in util.env(cr)['stock.move.line'].search(dom):
        move_line.write({'picking_id': move_line.move_id.picking_id.id})

def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {
        '9ca73322-2150-11e4-8c53-22000a4ac298': _db_epictv,
    })

