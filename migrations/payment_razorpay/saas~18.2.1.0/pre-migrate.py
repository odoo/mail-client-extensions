from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "payment_razorpay.payment_provider_form_razorpay_oauth")
