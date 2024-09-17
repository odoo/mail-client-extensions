from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "mail.ir_rule_discuss_channel_all")
    util.update_record_from_xml(cr, "mail.ir_rule_discuss_channel_member_is_self_all")
    util.update_record_from_xml(cr, "mail.ir_rule_discuss_channel_member_read_all")
