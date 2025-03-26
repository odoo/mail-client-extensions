from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "payment.provider.onboarding.wizard")
    util.remove_field(cr, "res.company", "payment_onboarding_payment_method")
    util.remove_record(cr, "payment.onboarding_onboarding_step_payment_provider")
    util.remove_record(cr, "payment.action_activate_stripe")
