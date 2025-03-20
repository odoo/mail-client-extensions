from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(
        cr, "im_livechat.ir_rule_discuss_channel_im_livechat_group_user", fields=["name", "groups"]
    )
    util.update_record_from_xml(
        cr, "im_livechat.ir_rule_discuss_channel_member_im_livechat_group_user", fields=["name", "groups"]
    )
