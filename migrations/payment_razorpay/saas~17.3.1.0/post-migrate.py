from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "payment.payment_provider_razorpay")
