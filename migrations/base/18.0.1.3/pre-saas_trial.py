from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "saas_website_onboarding.onboarding_onboarding_step_custom_domain")
