from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "payment_authorize.payment_acquirer_form", "payment_authorize.payment_provider_form")
