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

    util.create_m2m(
        cr, "im_livechat_channel_member_history_discuss_channel_agent_rel", "discuss_channel", "res_partner"
    )
    util.create_m2m(
        cr, "im_livechat_channel_member_history_discuss_channel_customer_rel", "discuss_channel", "res_partner"
    )
    util.create_column(cr, "discuss_channel", "livechat_is_escalated", "boolean", default=False)
