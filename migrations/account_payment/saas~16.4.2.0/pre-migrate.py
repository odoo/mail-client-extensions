from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_payment.account_payment_onboarding_panel")
    util.remove_view(cr, "account_payment.payment_onboarding_step")
