from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "payment_payulatam.payment_acquirer_form", "payment_payulatam.payment_provider_form")
