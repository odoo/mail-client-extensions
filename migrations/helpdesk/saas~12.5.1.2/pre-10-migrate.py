# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "helpdesk_team", "allow_portal_ticket_closing", "boolean")
    util.create_column(cr, "helpdesk_team", "use_helpdesk_sale_timesheet", "boolean")
    util.create_column(cr, "helpdesk_stage", "legend_blocked", "varchar")
    util.create_column(cr, "helpdesk_stage", "legend_done", "varchar")
    util.create_column(cr, "helpdesk_stage", "legend_normal", "varchar")
    util.rename_field(cr, "helpdesk.ticket", "partner_tickets", "partner_ticket_count")
    util.create_column(cr, "helpdesk_ticket", "closed_by_partner", "boolean")
    util.create_column(cr, "helpdesk_ticket", "sla_reached_late", "boolean")
    util.create_column(cr, "helpdesk_ticket", "date_last_stage_update", "timestamp without time zone")
    # util.create_m2m(cr, "helpdesk_sla_status", "helpdesk_ticket", "helpdesk_sla", "ticket_id", "sla_id")
    util.rename_field(cr, "helpdesk.ticket", "deadline", "sla_deadline")

    cr.execute(
        """
        UPDATE helpdesk_stage
           SET legend_blocked='Blocked',
               legend_done='Ready for Next Stage',
               legend_normal='In Progress'
    """
    )
    cr.execute("""
        CREATE TABLE helpdesk_sla_status (
            id SERIAL PRIMARY KEY,
            create_uid integer,
            create_date timestamp without time zone,
            write_uid integer,
            write_date timestamp without time zone,
            ticket_id int4,
            sla_id int4,
            sla_stage_id int4,
            deadline timestamp without time zone,
            reached_datetime timestamp without time zone,
            exceeded_days float8
        )
    """)
    cr.execute(
        """
   INSERT INTO helpdesk_sla_status
               (ticket_id, sla_id, deadline, sla_stage_id)
        SELECT t.id, s.id, t.sla_deadline, s.stage_id
          FROM helpdesk_ticket t
    INNER JOIN helpdesk_sla s on t.sla_id=s.id
    """
    )
    # cr.execute(
    #     """
    #         SELECT ticket_id, COUNT(id) AS reached_late_count
    #           FROM helpdesk_sla_status
    #          WHERE ticket_id IN %s AND deadline < reached_datetime
    #       GROUP BY ticket_id
    #     """
    # )
    util.remove_field(cr, "helpdesk.ticket", "sla_id")
    util.remove_field(cr, "helpdesk.ticket", "sla_name")
    util.remove_field(cr, "helpdesk.ticket", "sla_active")
    util.remove_field(cr, "helpdesk.ticket", "sla_fail")
