from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "payment_adyen.payment_acquirer_form", "payment_adyen.payment_provider_form")
