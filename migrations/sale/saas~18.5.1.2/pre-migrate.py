from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "sale.payment.provider.onboarding.wizard")
