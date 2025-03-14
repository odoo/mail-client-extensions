from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "website_payment.donation_mail_body", util.update_record_from_xml)
