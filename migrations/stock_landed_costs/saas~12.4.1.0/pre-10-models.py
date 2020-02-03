# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, "stock_valuation_layer", "stock_landed_cost_id", "int4")

    util.remove_field(cr, "stock.move", "landed_cost_value")
