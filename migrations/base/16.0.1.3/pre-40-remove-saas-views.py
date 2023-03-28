from odoo.upgrade import util


def migrate(cr, version):
    # saas views will be re-created post upgrade in saas
    util.remove_view(cr, "saas_payment_stripe.payment_acquirer_form")
