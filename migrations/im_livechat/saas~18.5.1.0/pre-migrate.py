from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "im_livechat.channel", "buffer_time")
    util.remove_field(cr, "discuss.channel", "anonymous_name")
    util.create_m2m(
        cr,
        "im_livechat_channel_member_history_discuss_channel_bot_rel",
        "discuss_channel",
        "res_partner",
    )
    if util.table_exists(cr, "im_livechat_expertise"):
        util.create_m2m(
            cr,
            "discuss_channel_im_livechat_expertise_rel",
            "discuss_channel",
            "im_livechat_expertise",
        )
    if util.table_exists(cr, "im_livechat_channel_member_history"):
        populate_bot_rel_query = """
          INSERT INTO im_livechat_channel_member_history_discuss_channel_bot_rel(discuss_channel_id, res_partner_id)
               SELECT h.channel_id, h.partner_id
                 FROM im_livechat_channel_member_history h
                WHERE h.livechat_member_type = 'bot'
        """
        util.explode_execute(cr, populate_bot_rel_query, "im_livechat_channel_member_history", alias="h")
        populate_expertise_rel_query = """
          INSERT INTO discuss_channel_im_livechat_expertise_rel(discuss_channel_id, im_livechat_expertise_id)
               SELECT h.channel_id, rel.im_livechat_expertise_id
                 FROM im_livechat_channel_member_history_im_livechat_expertise_rel rel
                 JOIN im_livechat_channel_member_history h
                   ON h.id = rel.im_livechat_channel_member_history_id
          """
        util.explode_execute(cr, populate_expertise_rel_query, "im_livechat_channel_member_history", alias="h")

    util.convert_field_to_html(cr, "chatbot.script.step", "message")
    util.remove_field(cr, "mail.message", "parent_author_name")
    util.remove_field(cr, "mail.message", "parent_body")
