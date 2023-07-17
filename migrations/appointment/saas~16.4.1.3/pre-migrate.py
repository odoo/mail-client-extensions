# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    for pre, post in [
        ("appointment_onboarding_panel", "onboarding_onboarding_appointment"),
        ("calendar_event_action_reporting", "calendar_event_action_appointment_reporting"),
        ("calendar_event_action_report", "calendar_event_action_report_all"),
    ]:
        util.rename_xmlid(cr, f"appointment.{pre}", f"appointment.{post}")

    # appointment type action revamp (gantt)
    util.remove_menus(cr, [util.ref(cr, "appointment.menu_appointment_booking")])
    util.remove_record(cr, "appointment.calendar_event_action_view_bookings")

    # computed stored column, computed in post-migrate
    util.create_column(cr, "calendar_event", "appointment_resource_id", "int4")

    util.remove_record(cr, "appointment.module_category_calendar")

    util.if_unchanged(cr, "appointment.calendar_event_type_data_online_appointment", util.update_record_from_xml)
