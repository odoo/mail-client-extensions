# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "event_registration", "event_begin_date", "timestamp without time zone")
    cr.execute(
        """
        UPDATE event_registration r
           SET event_begin_date = e.date_begin
          FROM event_event e
         WHERE e.id = r.event_id
    """
    )
