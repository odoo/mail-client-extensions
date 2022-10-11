from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "payment_paypal.payment_acquirer_form", "payment_paypal.payment_provider_form")
