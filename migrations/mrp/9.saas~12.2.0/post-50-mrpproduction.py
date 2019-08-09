# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    env = util.env(cr)
    cr.execute(
        """
        UPDATE mrp_production m
           SET procurement_group_id=po.group_id
          FROM procurement_order po
         WHERE po.production_id=m.id
           AND po.group_id IS NOT NULL
    """)
    cr.execute("""
        SELECT m.id,m.name
          FROM mrp_production m
         WHERE procurement_group_id IS NULL
    """)
    for mid,mo_name in cr.fetchall():
        procurement_group_id = env["procurement.group"].create({'name': mo_name})
        cr.execute("""
            UPDATE  mrp_production m
              SET procurement_group_id=%s
            WHERE id=%s
        """,[procurement_group_id.id,mid])

