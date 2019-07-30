# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "event_registration", "campaign_id", "int4")
    util.create_column(cr, "event_registration", "source_id", "int4")
    util.create_column(cr, "event_registration", "medium_id", "int4")
    cr.execute(
        """
        UPDATE event_registration
           SET campaign_id=so.campaign_id,
               source_id=so.source_id,
               medium_id=so.medium_id
          FROM sale_order so
         WHERE so.id=event_registration.sale_order_id
        """
    )
