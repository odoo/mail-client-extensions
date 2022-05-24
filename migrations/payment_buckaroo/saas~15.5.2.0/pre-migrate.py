from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "payment_buckaroo.payment_acquirer_form", "payment_buckaroo.payment_provider_form")
