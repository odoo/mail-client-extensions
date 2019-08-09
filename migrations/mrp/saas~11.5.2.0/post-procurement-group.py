# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    env = util.env(cr)
    cr.execute("""
        SELECT m.id,m.name
          FROM mrp_production m
          JOIN procurement_group pg on m.procurement_group_id = pg.id
         WHERE pg.sale_id IS NOT NULL
    """)
    for mid,mo_name in cr.fetchall():
        procurement_group_id = env["procurement.group"].create({'name': mo_name})
        cr.execute("""
            UPDATE  mrp_production m
              SET procurement_group_id=%s
            WHERE id=%s
        """,[procurement_group_id.id,mid])

