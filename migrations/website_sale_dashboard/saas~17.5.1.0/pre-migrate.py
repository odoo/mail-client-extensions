from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "website_sale_dashboard.onboarding_onboarding_step_payment_provider")
    util.remove_record(cr, "website_sale_dashboard.onboarding_onboarding_website_sale_dashboard")
