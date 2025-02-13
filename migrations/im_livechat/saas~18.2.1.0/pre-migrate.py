from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "im_livechat_channel_rule", "chatbot_enabled_condition", "varchar", default="always")

    def adapter(leaf, _, __):
        left, operator, right = leaf
        operator = "=" if bool(right) else "!="
        return [(left, operator, "only_if_no_operator")]

    util.update_field_usage(
        cr,
        "im_livechat.channel.rule",
        "chatbot_only_if_no_operator",
        "chatbot_enabled_condition",
        domain_adapter=adapter,
    )
    cr.execute("""
        UPDATE im_livechat_channel_rule
           SET chatbot_enabled_condition = 'only_if_no_operator'
         WHERE chatbot_only_if_no_operator = True
    """)
    util.remove_field(cr, "im_livechat.channel.rule", "chatbot_only_if_no_operator")
