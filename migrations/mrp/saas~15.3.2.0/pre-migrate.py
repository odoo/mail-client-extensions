# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Non-stored computed m2m replaced with a related m2o
    util.rename_field(cr, "stock.move", "order_finished_lot_ids", "order_finished_lot_id")
    util.create_column(cr, "stock_move", "order_finished_lot_id", "int4")
    query = """
        UPDATE stock_move m
           SET order_finished_lot_id = p.lot_producing_id
          FROM mrp_production p
         WHERE m.raw_material_production_id = p.id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="stock_move", alias="m"))
