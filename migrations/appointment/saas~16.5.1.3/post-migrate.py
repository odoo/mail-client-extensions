# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE appointment_type
        SET booked_mail_template_id=%s,
            canceled_mail_template_id=%s
    """,
        [
            util.ref(cr, "appointment.attendee_invitation_mail_template"),
            util.ref(cr, "appointment.appointment_canceled_mail_template"),
        ],
    )

    # Filling empty new field appointment_booker_id
    query = """
        WITH events_partners AS (
            SELECT DISTINCT ON (e.id)
                   e.id AS event_id,
                   epr.res_partner_id AS partner_id
              FROM calendar_event e
              JOIN calendar_event_res_partner_rel AS epr
                ON e.id = epr.calendar_event_id
         LEFT JOIN res_users AS ep_user
                ON e.user_id = ep_user.id
         LEFT JOIN res_users AS ep_create_user
                ON e.create_uid = ep_create_user.id
             WHERE {parallel_filter}
               AND e.appointment_type_id IS NOT NULL
               AND e.start > NOW()
          ORDER BY e.id,
                   -- if the partner that created the event is linked we take it
                   epr.res_partner_id IS DISTINCT FROM ep_create_user.partner_id,
                   -- otherwise take first partner that is not responsible
                   epr.res_partner_id IS NOT DISTINCT FROM ep_user.partner_id,
                   -- tie breaker
                   epr.res_partner_id
        )
        UPDATE calendar_event e
           SET appointment_booker_id = ep.partner_id
          FROM events_partners ep
         WHERE e.id = ep.event_id
    """
    util.explode_execute(cr, query, table="calendar_event", alias="e")
