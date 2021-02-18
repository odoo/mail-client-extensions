# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "pos_config", "ship_later", "boolean", default=False)
    util.create_column(cr, "pos_config", "warehouse_id", "int4")
    util.create_column(cr, "pos_config", "route_id", "int4")
    util.create_column(cr, "pos_config", "picking_policy", "varchar", default="direct")

    util.create_column(cr, "pos_order", "procurement_group_id", "int4")
    util.create_column(cr, "pos_order", "to_ship", "boolean", default=False)
