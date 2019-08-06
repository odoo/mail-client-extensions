# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    for table in ("mrp_workorder", "mrp_product_produce", "mrp_bom"):
        util.create_column(cr, table, "consumption", "varchar")
        cr.execute("update %s set consumption='strict'" % table)

    util.remove_field(cr, "mrp.routing", "location_id")
    util.remove_field(cr, "mrp.workorder", "workorder_line_ids")

    util.rename_field(cr, "mrp.workorder.line", "raw_workorder_id", "workorder_id")
    if util.table_exists(cr, 'mrp_workorder_line'):
        util.create_column(cr, "mrp_workorder_line", "finished_workorder_id", "int4")

    util.rename_field(cr, 'res.config.settings', 'module_mrp_byproduct', 'group_mrp_byproducts')
    util.create_column(cr, 'res_config_settings', 'module_mrp_subcontracting', 'boolean')

    util.create_m2m(cr, 'stock_move_line_stock_production_lot_rel', 'stock_move_line', 'stock_production_lot')
    cr.execute("""
        INSERT INTO stock_move_line_stock_production_lot_rel (stock_move_line_id, stock_production_lot_id)
             SELECT id, lot_produced_id
               FROM stock_move_line
              WHERE lot_produced_id IS NOT NULL
    """)
    util.remove_field(cr, 'stock.move.line', 'lot_produced_id')

    if util.table_exists(cr, 'mrp_subproduct'):
        util.rename_model(cr, 'mrp.subproduct', 'mrp.bom.byproduct')
        util.rename_field(cr, 'stock.move', 'subproduct_id', 'byproduct_id')

    util.create_column(cr, 'stock_picking_type', 'use_create_components_lots', 'int4')
    util.remove_field(cr, 'stock_production_lot', 'use_next_on_work_order_id')

    util.rename_field(cr, "mrp.product.produce.line", "product_produce_id", "raw_product_produce_id")
    util.create_column(cr, "mrp_product_produce_line", "finished_product_produce_id", "int4")
