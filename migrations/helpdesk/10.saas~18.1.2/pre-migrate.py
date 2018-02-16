# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'helpdesk_team', 'use_helpdesk_timesheet', 'boolean')
    cr.execute("UPDATE helpdesk_team SET use_helpdesk_timesheet=%s",
               [util.module_installed(cr, 'helpdesk_timesheet')])
    util.rename_field(cr, 'helpdesk.team', 'use_website_helpdesk_rating', 'portal_show_rating')

    util.remove_field(cr, 'helpdesk.sla', 'time_minutes')

    util.create_column(cr, 'helpdesk_ticket', 'access_token', 'varchar')
    cr.execute("""
        UPDATE helpdesk_ticket
           SET access_token = md5(md5(random()::varchar || id::varchar) || clock_timestamp()::varchar)::uuid::varchar
         WHERE access_token IS NULL
    """)

    # merge portal access from website_helpdesk
    util.move_field_to_module(cr, 'helpdesk.team', 'website_rating_url', 'website_helpdesk', 'helpdesk')
    util.move_field_to_module(cr, 'helpdesk.team', 'access_token', 'website_helpdesk', 'helpdesk')

    xids = util.splitlines("""
        helpdesk_portal_ticket_rule
        access_helpdesk_ticket_portal
        access_helpdesk_stage_portal

        portal_my_home_menu_helpdesk
        portal_my_home_helpdesk_ticket
        portal_helpdesk_ticket
        tickets_followup
        index
        team_rating_progress_data
        team_rating_data
        team_rating_team
    """)

    for x in xids:
        util.rename_xmlid(cr, 'website_helpdesk.' + x, 'helpdesk.' + x)
