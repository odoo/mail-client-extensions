# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # planning_slot
    util.create_column(cr, "planning_slot", "sale_line_id", "int4")
    util.create_column(cr, "planning_slot", "sale_order_id", "int4")
    # don't we need to drop the not null constraint on start_datetime, end_datetime ?

    # product_template
    util.create_column(cr, "product_template", "planning_enabled", "boolean", default=False)
    util.create_column(cr, "product_template", "planning_role_id", "int4")

    # sale_order_line
    util.create_column(cr, "sale_order_line", "planning_hours_to_plan", "float8", default=0)
    util.create_column(cr, "sale_order_line", "planning_hours_planned", "float8", default=0)
