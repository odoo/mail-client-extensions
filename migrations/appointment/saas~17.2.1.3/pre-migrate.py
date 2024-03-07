# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "appointment.appointment_onboarding_create_appointment_type_step")
    util.remove_record(cr, "appointment.appointment_onboarding_preview_invite_step")
    util.remove_record(cr, "appointment.appointment_onboarding_configure_calendar_provider_step")
    util.remove_record(cr, "appointment.onboarding_onboarding_appointment")

    util.remove_record(cr, "appointment.access_appointment_onboarding_link_all")
    util.remove_record(cr, "appointment.access_appointment_onboarding_link_user")
    util.remove_record(cr, "appointment.access_appointment_onboarding_link_manager")

    util.remove_view(cr, "appointment.appointment_type_view_form_appointment_onboarding")
    util.remove_view(cr, "appointment.appointment_onboarding_link_view_form")

    util.remove_model(cr, "appointment.onboarding.link")

    if util.module_installed(cr, "appointment_hr"):
        util.move_field_to_module(cr, "calendar.event", "partners_on_leave", "appointment_hr", "appointment")
        util.rename_field(cr, "calendar.event", "partners_on_leave", "on_leave_partner_ids")
    util.rename_field(cr, "calendar.event", "resources_on_leave", "on_leave_resource_ids")

    util.remove_constraint(cr, "calendar_event", "check_resource_and_appointment_type")
    util.remove_field(cr, "calendar.event", "appointment_resource_id")
