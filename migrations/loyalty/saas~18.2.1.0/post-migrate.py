from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "loyalty.mail_template_loyalty_card", util.update_record_from_xml)
