from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "account_payment.onboarding_onboarding_step_payment_provider")
