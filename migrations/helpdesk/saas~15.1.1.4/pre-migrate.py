# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "helpdesk_team", "privacy_visibility", "character varying", default="internal")
    cr.execute(
        """
           UPDATE helpdesk_team h
              SET privacy_visibility='invited_internal'
             FROM helpdesk_visibility_team v
            WHERE v.helpdesk_team_id=h.id
        """
    )

    util.remove_field(cr, "helpdesk.team", "visibility_member_ids")
    util.remove_field(cr, "helpdesk.team", "privacy")

    util.create_m2m(cr, "helpdesk_sla_helpdesk_ticket_type_rel", "helpdesk_sla", "helpdesk_ticket_type")
    cr.execute(
        """
            INSERT INTO helpdesk_sla_helpdesk_ticket_type_rel(helpdesk_sla_id, helpdesk_ticket_type_id)
                SELECT id, ticket_type_id
                    FROM helpdesk_sla
                    WHERE ticket_type_id IS NOT NULL
        """
    )
    util.update_field_usage(cr, "helpdesk.sla", "ticket_type_id", "ticket_type_ids")
    util.remove_field(cr, "helpdesk.sla", "ticket_type_id")

    util.create_column(cr, "helpdesk_ticket", "ticket_ref", "varchar")
    cr.execute("UPDATE helpdesk_ticket t SET ticket_ref = t.id")

    util.rename_field(cr, "helpdesk.team", "upcoming_sla_fail_tickets", "sla_failed")
    util.remove_record(cr, "helpdesk.action_upcoming_sla_fail_all_tickets")
