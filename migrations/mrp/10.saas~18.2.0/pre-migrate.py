# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # eb = util.expand_braces
    # util.rename_field(cr, 'mrp.config.settings', *eb('{default_,}use_manufacturing_lead'))

    # util.create_column(cr, 'mrp_workorder', 'product_id', 'int4')
    # cr.execute("""
    #     UPDATE mrp_workorder w
    #        SET product_id = p.product_id
    #       FROM mrp_production p
    #      WHERE p.id = w.production_id
    # """)

    # util.create_column(cr, 'stock_move_line', 'workorder_id', 'int4')
    # util.create_column(cr, 'stock_move_line', 'production_id', 'int4')
    # util.create_column(cr, 'stock_move_line', 'lot_produced_id', 'int4')
    # util.create_column(cr, 'stock_move_line', 'lot_produced_qty', 'float8')
    # util.create_column(cr, 'stock_move_line', 'done_wo', 'boolean')
    # util.create_column(cr, 'stock_move_line', 'done_move', 'boolean')

    # util.rename_field(cr, 'mrp.workorder', 'move_lot_ids', 'move_line_ids')
    # util.rename_field(cr, 'mrp.workorder', 'active_move_lot_ids', 'active_move_line_ids')
    raise util.MigrationError('WIP')
