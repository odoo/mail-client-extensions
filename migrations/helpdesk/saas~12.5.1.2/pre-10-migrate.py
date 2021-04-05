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
    cr.execute(
        """
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
    """
    )
    cr.execute(
        """
   INSERT INTO helpdesk_sla_status
               (ticket_id, sla_id, deadline, sla_stage_id)
        SELECT t.id, s.id, t.sla_deadline, s.stage_id
          FROM helpdesk_ticket t
    INNER JOIN helpdesk_sla s on t.sla_id=s.id
    """
    )
    cr.execute(
        """
        UPDATE helpdesk_ticket t
           SET sla_deadline=NULL
          FROM helpdesk_stage stage
         WHERE t.stage_id = stage.id
           AND stage.is_close='t'
    """
    )
    cr.execute(
        """
        WITH extracted_date AS
            (
            SELECT DISTINCT ON (status.id)
               status.id,
               msg.date
              FROM helpdesk_sla_status status
              JOIN helpdesk_ticket t ON status.ticket_id = t.id
              JOIN helpdesk_stage stage ON status.sla_stage_id = stage.id
              JOIN mail_message msg ON (t.id = msg.res_id AND msg.model = 'helpdesk.ticket')
              JOIN mail_message_subtype msg_subtype ON (msg.subtype_id = msg_subtype.id AND msg_subtype.name = 'Stage Changed')
              JOIN mail_tracking_value track ON (msg.id = track.mail_message_id AND track.field = 'stage_id')
              JOIN helpdesk_stage other_stage ON track.new_value_integer = other_stage.id
             WHERE (stage.id = track.new_value_integer OR stage.sequence <= other_stage.sequence)
          GROUP BY status.id, msg.date
          ORDER BY status.id, msg.date DESC
            )
        UPDATE helpdesk_sla_status status
           SET reached_datetime = extracted_date.date
          FROM extracted_date
         WHERE status.id = extracted_date.id
    """
    )
    cr.execute(
        """
        WITH compute_sla_reached_late AS
            (
            SELECT t.id AS ticket_id
              FROM helpdesk_ticket t
              JOIN helpdesk_sla_status status ON t.id = status.ticket_id
             WHERE status.deadline < status.reached_datetime
          GROUP BY t.id
            HAVING COUNT(status.id) > 0
            )
        UPDATE helpdesk_ticket t
           SET sla_reached_late = True
          FROM compute_sla_reached_late c
         WHERE t.id = c.ticket_id
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
    util.remove_column(cr, "helpdesk_ticket", "sla_fail")  # related not stored

    util.remove_record(cr, "helpdesk.helpdesk_sla_cron")
    util.remove_record(cr, "helpdesk.helpdesk_sla_cron_ir_actions_server")

    for field, value in [
        ("helpdesk_target_closed", 1),
        ("helpdesk_target_rating", 100),
        ("helpdesk_target_success", 100),
    ]:
        cr.execute(f"UPDATE res_users set {field}={value} WHERE COALESCE({field}, 0) <= 0")

    cr.execute(
        """
            WITH updated AS (
                   UPDATE helpdesk_team team
                      SET company_id = u.company_id
                     FROM res_users u
                    WHERE u.id = COALESCE(team.write_uid, team.create_uid, 1)
                      AND team.company_id IS NULL
                RETURNING team.id as team_id, team.company_id as company_id
            )
            UPDATE helpdesk_ticket ticket
               SET company_id = updated.company_id
              FROM updated
             WHERE updated.team_id = ticket.team_id
        """
    )
    cr.execute(
        "UPDATE ir_ui_menu SET action = NULL WHERE id = %s",
        [util.ref(cr, "helpdesk.helpdesk_ticket_menu_main")],
    )
