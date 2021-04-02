# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "mrp_routing_workcenter", "active", "boolean", default=True)
