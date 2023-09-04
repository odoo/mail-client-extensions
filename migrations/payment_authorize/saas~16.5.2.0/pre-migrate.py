from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "payment.provider", "authorize_payment_method_type")
    util.remove_field(cr, "payment.token", "authorize_payment_method_type")
