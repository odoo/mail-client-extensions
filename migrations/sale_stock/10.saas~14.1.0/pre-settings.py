# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    fields = util.splitlines("""
        default_picking_policy
        group_mrp_properties
        group_route_so_lines
        module_sale_order_dates
    """)
    for f in fields:
        util.remove_field(cr, 'sale.config.settings', f)
