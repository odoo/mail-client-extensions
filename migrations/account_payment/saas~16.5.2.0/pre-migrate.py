from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_payment.payment_checkout_inherit")
    util.remove_view(cr, "account_payment.payment_manage_inherit")
