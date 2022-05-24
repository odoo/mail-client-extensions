from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "payment_mollie.payment_acquirer_form", "payment_mollie.payment_provider_form")
