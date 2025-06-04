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
    query = """
        INSERT INTO im_livechat_channel_member_history_discuss_channel_agent_rel(discuss_channel_id, res_partner_id)
             SELECT id, livechat_operator_id
               FROM discuss_channel
              WHERE channel_type = 'livechat'
                AND livechat_operator_id IS NOT NULL
              UNION
             SELECT c.id, sc.operator_partner_id
               FROM chatbot_message m
               JOIN discuss_channel c
                 ON c.id = m.discuss_channel_id
               JOIN chatbot_script_step st
                 ON st.id = m.script_step_id
               JOIN chatbot_script sc
                 ON sc.id = st.chatbot_script_id
              WHERE c.channel_type = 'livechat'
    """
    cr.execute(query)

    util.create_m2m(
        cr, "im_livechat_channel_member_history_discuss_channel_customer_rel", "discuss_channel", "res_partner"
    )
    if util.column_exists(cr, "discuss_channel", "livechat_visitor_id"):  # from `website_livechat` module
        query = """
            INSERT INTO im_livechat_channel_member_history_discuss_channel_customer_rel(discuss_channel_id, res_partner_id)
                 SELECT c.id, v.partner_id
                   FROM discuss_channel c
                   JOIN website_visitor v
                     ON v.id = c.livechat_visitor_id
                  WHERE c.channel_type = 'livechat'
                    AND v.partner_id IS NOT NULL
        """
        cr.execute(query)

    util.create_column(cr, "discuss_channel", "livechat_is_escalated", "boolean", default=False)
