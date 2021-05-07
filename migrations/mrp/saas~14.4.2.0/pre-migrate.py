# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "mrp_routing_workcenter", "active", "boolean", default=True)
    util.convert_field_to_html(cr, "mrp.workcenter", "note")
    util.convert_field_to_html(cr, "mrp.routing.workcenter", "note")
