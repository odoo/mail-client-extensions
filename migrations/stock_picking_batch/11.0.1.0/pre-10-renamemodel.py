# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_model(cr, 'stock.picking.wave', 'stock.picking.batch')
    util.rename_field(cr, 'stock.picking', 'wave_id', 'batch_id')
    
    # Rename xml ids as they were all renamed
    util.rename_xmlid(cr, 'stock_picking_batch.view_picking_wave_form', 'stock_picking_batch.stock_picking_batch_form')
    util.rename_xmlid(cr, 'stock_picking_batch.view_picking_wave_tree', 'stock_picking_batch.stock_picking_batch_tree')
    util.rename_xmlid(cr, 'stock_picking_batch.view_picking_wave_filter', 'stock_picking_batch.stock_picking_batch_filter')
    util.rename_xmlid(cr, 'stock_picking_batch.view_stock_picking_wave_tree_inherit', 'stock_picking_batch.vpicktree_inherit_stock_picking_batch')
    util.remove_record(cr, 'stock_picking_batch.view_stock_picking_wave_inherit')
    util.rename_xmlid(cr, 'stock_picking_batch.view_stock_picking_wave_search_inherit', 'stock_picking_batch.view_picking_internal_search_inherit_stock_picking_batch')
    util.rename_xmlid(cr, 'stock_picking_batch.view_stock_picking_wave_inherit', 'stock_picking_batch.stock_picking_batch_menu')
    util.rename_xmlid(cr, 'stock_picking_batch.action_picking_wave', 'stock_picking_batch.stock_picking_batch_action')
