from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "payment_alipay.payment_acquirer_form", "payment_alipay.payment_provider_form")
