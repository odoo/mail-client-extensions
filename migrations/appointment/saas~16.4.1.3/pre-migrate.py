# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "appointment.appointment_onboarding_panel", "appointment.onboarding_onboarding_appointment")

    # appointment type action revamp (gantt)
    util.remove_menus(cr, [util.ref(cr, "appointment.menu_appointment_booking")])
    util.remove_record(cr, "appointment.calendar_event_action_view_bookings")

    # computed stored column, computed in post-migrate
    util.create_column(cr, "calendar_event", "appointment_resource_id", "int4")
