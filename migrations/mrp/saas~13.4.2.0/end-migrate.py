# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    env = util.env(cr)
    env["mrp.production"].search(
        [("state", "in", ("draft", "confirmed")), ("bom_id", "!=", False), ("workorder_ids", "=", False)]
    )._create_workorder()

    # For MO in progress (where qty_produced is > 0), because move_finished is already created (old version),
    # It will be problematic in the new mrp version.
    # => Automatically create the backorder of the MO if qty_produced > 0 and state = progress
    # OR
    # => Remove finished stock move line (mo.product_id = move_line.product_id) and they will be recreate when the MO will be closed
    # TODO
    cr.execute("SELECT id FROM stock_move WHERE raw_material_production_id IS NOT NULL OR production_id IS NOT NULL")
    ids_recompute_stock_move = [id for id, in cr.fetchall()]
    util.recompute_fields(cr, "stock.move", ["unit_factor", "reference"], ids=ids_recompute_stock_move)

    util.recompute_fields(cr, "mrp.production", ["state", "production_location_id"])
