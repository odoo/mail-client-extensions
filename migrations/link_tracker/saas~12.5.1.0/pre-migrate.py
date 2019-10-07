# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "link_tracker_click", "campaign_id", "int4")
    cr.execute("""
        UPDATE link_tracker_click c
           SET campaign_id = l.campaign_id
          FROM link_tracker l
         WHERE l.id = c.link_id
    """)
