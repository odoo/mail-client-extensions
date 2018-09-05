# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
           update stock_picking p
            set sale_id = g.sale_id
           from procurement_group g
           where g.id = p.group_id
           and p.group_id is not null
    """)
