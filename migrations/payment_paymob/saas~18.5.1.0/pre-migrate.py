from odoo.upgrade import util


def migrate(cr, version):
    # === PAYMENT PROVIDER === #

    util.remove_field(cr, "payment.provider", "paymob_access_token")
    util.remove_field(cr, "payment.provider", "paymob_access_token_expiry")
