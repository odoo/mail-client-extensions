from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "mail.ir_rule_mail_canned_response_admin", util.update_record_from_xml)
