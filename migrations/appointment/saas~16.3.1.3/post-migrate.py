from odoo.upgrade import util


def migrate(cr, version):
    for onboarding_step_id in (
        "appointment.appointment_onboarding_create_appointment_type_step",
        "appointment.appointment_onboarding_preview_invite_step",
        "appointment.appointment_onboarding_configure_calendar_provider_step",
    ):
        util.if_unchanged(cr, onboarding_step_id, util.update_record_from_xml)
