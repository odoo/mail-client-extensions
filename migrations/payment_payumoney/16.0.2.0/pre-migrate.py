from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "payment_payumoney.payment_acquirer_form", "payment_payumoney.payment_provider_form")
