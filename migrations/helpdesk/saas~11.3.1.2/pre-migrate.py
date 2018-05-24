# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_record(cr, "helpdesk.mt_ticket_assigned")
    util.remove_record(cr, "helpdesk.mt_team_ticket_assigned")

    util.create_column(cr, "helpdesk_team", "resource_calendar_id", "int4")
    cr.execute("""
        UPDATE helpdesk_team t
           SET resource_calendar_id = c.resource_calendar_id
          FROM res_company c
         WHERE c.id = t.company_id
    """)
