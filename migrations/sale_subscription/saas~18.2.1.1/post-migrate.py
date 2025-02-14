from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "sale_subscription.email_payment_close", util.update_record_from_xml)
    util.if_unchanged(cr, "sale_subscription.email_payment_reminder", util.update_record_from_xml)
