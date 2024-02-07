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
