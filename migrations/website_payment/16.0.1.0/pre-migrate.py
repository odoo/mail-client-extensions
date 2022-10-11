from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "res.config.settings", "acquirers_state", "providers_state")
    util.rename_xmlid(cr, "website_payment.acquirer_form_website", "website_payment.payment_provider_form")
