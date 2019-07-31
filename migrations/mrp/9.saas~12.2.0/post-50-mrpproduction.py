# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE mrp_production m
           SET procurement_group_id=po.group_id
          FROM procurement_order po
         WHERE po.production_id=m.id
           AND po.group_id IS NOT NULL
    """)
