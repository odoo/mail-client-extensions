from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "payment.payment_method_amazon_pay", util.update_record_from_xml)
    util.if_unchanged(cr, "payment.payment_provider_stripe", util.update_record_from_xml)
