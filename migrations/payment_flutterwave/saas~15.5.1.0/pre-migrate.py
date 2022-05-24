from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "payment_flutterwave.payment_acquirer_form", "payment_flutterwave.payment_provider_form")
