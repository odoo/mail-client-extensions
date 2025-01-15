from odoo.upgrade.util import remove_record


def migrate(cr, version):
    remove_record(cr, "website_payment.s_donation_000_js")
