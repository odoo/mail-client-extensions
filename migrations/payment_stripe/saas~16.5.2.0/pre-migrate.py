from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "payment_stripe.checkout")
    util.remove_view(cr, "payment_stripe.manage")
