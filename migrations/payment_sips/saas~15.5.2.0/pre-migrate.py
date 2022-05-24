from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "payment_sips.payment_acquirer_form", "payment_sips.payment_provider_form")
