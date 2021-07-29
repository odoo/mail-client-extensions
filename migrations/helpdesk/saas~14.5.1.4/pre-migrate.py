# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "helpdesk.ticket", "commercial_partner_id", "helpdesk_sale", "helpdesk")
    util.create_column(cr, "helpdesk_team", "privacy", "varchar", default="user")
    cr.execute(
        """
            UPDATE helpdesk_team t
                SET privacy = 'invite'
              FROM helpdesk_visibility_team v
            WHERE v.helpdesk_team_id=t.id
        """
    )
    util.move_field_to_module(cr, "helpdesk.team", "use_fsm", "helpdesk_fsm", "helpdesk")
    util.create_column(cr, "helpdesk_team", "use_fsm", "bool")
    util.remove_field(cr, "helpdesk.ticket", "is_self_assigned")
    util.remove_field(cr, "helpdesk.team", "portal_rating_url")

    helpdesk_user_group_id = util.ref(cr, "helpdesk.group_helpdesk_user")
    # add users from visibility_member_ids if member_ids is empty.
    cr.execute(
        """
            INSERT INTO helpdesk_team_res_users_rel(helpdesk_team_id, res_users_id)
            SELECT vt.helpdesk_team_id, vt.res_users_id
              FROM helpdesk_visibility_team vt
              JOIN helpdesk_team ht ON ht.id = vt.helpdesk_team_id
              JOIN res_company_users_rel rc ON rc.cid = ht.company_id AND rc.user_id = vt.res_users_id
              JOIN res_groups_users_rel rg ON rg.uid = vt.res_users_id AND rg.gid = %s
             WHERE ht.id NOT IN (SELECT helpdesk_team_id FROM helpdesk_team_res_users_rel GROUP BY helpdesk_team_id)

        """,
        [helpdesk_user_group_id],
    )
    # Add all users from the group 'helpdesk.group_helpdesk_user' for the team without access
    cr.execute(
        """
            INSERT INTO helpdesk_team_res_users_rel(helpdesk_team_id, res_users_id)
            SELECT ht.id, rg.uid
              FROM helpdesk_team ht
              JOIN res_groups_users_rel rg ON rg.gid = %s
              JOIN res_company_users_rel rc ON rc.cid = ht.company_id AND rc.user_id = rg.uid
             WHERE ht.id NOT IN (SELECT helpdesk_team_id FROM helpdesk_team_res_users_rel GROUP BY helpdesk_team_id)
        """,
        [helpdesk_user_group_id],
    )

    # Combine time_days, time_hours and time_minutes into a single field
    util.create_column(cr, "helpdesk_sla", "time", "float8", default=0)

    # Update helpdesk.sla table, just like before 1 day is not the equivalent of 24 hours, but one average working day
    # defaults to 8 hours per day in case no calendar can be found
    cr.execute(
        """
        WITH helper as (
            SELECT COALESCE(tc.hours_per_day, cc.hours_per_day, 8) as avg_hours,
                   sla.id
              FROM helpdesk_sla sla
              JOIN helpdesk_team htim ON htim.id = sla.team_id
              JOIN res_company cpny ON cpny.id = htim.company_id
         LEFT JOIN resource_calendar tc ON tc.id = htim.resource_calendar_id
         LEFT JOIN resource_calendar cc ON cc.id = cpny.resource_calendar_id
        )
        UPDATE helpdesk_sla sla
           SET time = ((time_days * hlp.avg_hours) + (time_hours) + (time_minutes / 60.0)) -- .0 to force float
          FROM helper hlp
         WHERE hlp.id = sla.id
    """
    )

    util.remove_field(cr, "helpdesk.sla", "time_days")
    util.remove_field(cr, "helpdesk.sla", "time_hours")
    util.remove_field(cr, "helpdesk.sla", "time_minutes")

    util.remove_record(cr, "helpdesk.helpdesk_ticket_team_analysis_action")

    for v in "graph_analysis cohort pivot_analysis".split():
        util.remove_view(cr, f"helpdesk.helpdesk_ticket_view_{v}")

    for x in "action_close_analysis action_7days_analysis analysis_action action_success action_7dayssuccess".split():
        util.force_noupdate(cr, f"helpdesk.helpdesk_ticket_{x}", False)

    util.remove_field(cr, "helpdesk.sla", "target_type")
    util.remove_field(cr, "helpdesk.sla.status", "target_type")

    util.remove_field(cr, "helpdesk.ticket", "attachment_number")
    util.remove_view(cr, "helpdesk.helpdesk_sla_report_analysis_view_tree")
