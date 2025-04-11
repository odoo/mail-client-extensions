from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr,
        "im_livechat.ir_rule_discuss_channel_group_im_livechat_group_manager",
        "im_livechat.ir_rule_discuss_channel_im_livechat_group_user",
    )
    util.rename_xmlid(
        cr,
        "im_livechat.ir_rule_discuss_channel_member_group_im_livechat_group_manager",
        "im_livechat.ir_rule_discuss_channel_member_im_livechat_group_user",
    )
    util.remove_field(cr, "im_livechat.report.channel", "technical_name")
