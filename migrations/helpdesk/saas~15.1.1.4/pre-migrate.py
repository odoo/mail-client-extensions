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

    cr.execute(
        """
        INSERT INTO mail_followers(res_model, res_id, partner_id)
        SELECT 'helpdesk.team', v.helpdesk_team_id, u.partner_id
          FROM helpdesk_visibility_team v
          JOIN res_users u ON u.id = v.res_users_id
        ON CONFLICT DO NOTHING
        """
    )

    cr.execute(
        """
        INSERT INTO mail_followers(res_model, res_id, partner_id)
        SELECT 'helpdesk.ticket', t.id, u.partner_id
          FROM helpdesk_ticket t
          JOIN helpdesk_visibility_team v ON t.team_id = v.helpdesk_team_id
          JOIN res_users u ON u.id = v.res_users_id
        ON CONFLICT DO NOTHING
        """
    )

    util.remove_field(cr, "helpdesk.team", "visibility_member_ids")
    util.remove_field(cr, "helpdesk.team", "privacy")

    cr.execute("UPDATE helpdesk_ticket SET priority = '0' WHERE priority = '1'")
    cr.execute("UPDATE helpdesk_sla SET priority = '0' WHERE priority = '1'")
    util.create_m2m(cr, "helpdesk_sla_helpdesk_ticket_type_rel", "helpdesk_sla", "helpdesk_ticket_type")
    cr.execute(
        """
            INSERT INTO helpdesk_sla_helpdesk_ticket_type_rel(helpdesk_sla_id, helpdesk_ticket_type_id)
                SELECT id, ticket_type_id
                    FROM helpdesk_sla
                    WHERE ticket_type_id IS NOT NULL
        """
    )
    util.update_field_references(cr, "ticket_type_id", "ticket_type_ids", only_models=("helpdesk.sla",))
    util.remove_field(cr, "helpdesk.sla", "ticket_type_id")

    util.create_column(cr, "helpdesk_ticket", "ticket_ref", "varchar")
    cr.execute("UPDATE helpdesk_ticket t SET ticket_ref = t.id")

    util.rename_field(cr, "helpdesk.team", "upcoming_sla_fail_tickets", "sla_failed")
    util.remove_record(cr, "helpdesk.action_upcoming_sla_fail_all_tickets")
