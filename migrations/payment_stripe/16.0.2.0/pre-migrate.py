from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("payment_stripe.payment_{acquirer,provider}_form"))
    util.rename_xmlid(cr, *eb("payment_stripe.action_payment_{acquirer,provider}_onboarding"))
