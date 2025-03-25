from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "sale_subscription.mail_template_subscription_rating", util.update_record_from_xml)
