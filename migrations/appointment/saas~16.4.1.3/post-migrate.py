# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    for onboarding_step_id in (
        "appointment.appointment_onboarding_create_appointment_type_step",
        "appointment.appointment_onboarding_preview_invite_step",
        "appointment.appointment_onboarding_configure_calendar_provider_step",
    ):
        util.if_unchanged(cr, onboarding_step_id, util.update_record_from_xml)

    # force upgrade of some records to be sure of their coherency with new menus / rules
    menu_xid = (
        "menu_appointment_type_custom" if util.version_gte("17.0") else "menu_appointment_type_custom_and_anytime"
    )
    for xml_id in (
        "menu_appointment_resource",
        menu_xid,
        "menu_appointment_invite",
        "group_appointment_manager",
    ):
        util.update_record_from_xml(cr, f"appointment.{xml_id}")

    # Populate appointment_resource_id for all events with a single booking line
    query = """
        WITH single_resource_appointment AS (
            SELECT abl.calendar_event_id,
                   MIN(abl.appointment_resource_id) AS appointment_resource_id
              FROM appointment_booking_line abl
              JOIN calendar_event e -- for // execute
                ON e.id = abl.calendar_event_id
             WHERE {parallel_filter}
             GROUP BY abl.calendar_event_id
            HAVING count(*) = 1
        ),
        single_resource_and_type AS (
             SELECT sra.calendar_event_id,
                    sra.appointment_resource_id,
                    MIN(r.appointment_type_id) AS appointment_type_id
               FROM single_resource_appointment sra
          LEFT JOIN appointment_type_appointment_resource_rel r
                 ON r.appointment_resource_id = sra.appointment_resource_id
              GROUP BY sra.calendar_event_id, sra.appointment_resource_id
        )
        UPDATE calendar_event e
           SET appointment_resource_id = srt.appointment_resource_id,
               appointment_type_id = COALESCE(e.appointment_type_id, srt.appointment_type_id)
          FROM single_resource_and_type srt
         WHERE e.id = srt.calendar_event_id
    """
    util.explode_execute(cr, query, table="calendar_event", alias="e")
