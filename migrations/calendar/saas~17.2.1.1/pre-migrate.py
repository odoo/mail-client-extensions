from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "calendar.onboarding_onboarding_step_setup_calendar_integration")
    util.remove_record(cr, "calendar.onboarding_onboarding_calendar")
