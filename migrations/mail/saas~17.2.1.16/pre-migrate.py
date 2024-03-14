from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "mail_shortcode", "is_shared", "boolean", default=True)
    util.rename_xmlid(cr, "im_livechat.mail_shortcode_data_hello", "mail.mail_canned_response_data_hello")
    util.rename_xmlid(cr, "im_livechat.mail_canned_response_bye", "mail.mail_canned_response_bye")
    util.rename_model(cr, "mail.shortcode", "mail.canned.response")
    util.remove_record(cr, "mail.mail_shortcode_action")
    util.remove_view(cr, "mail.mail_shortcode_view_search")
    util.remove_view(cr, "mail.mail_shortcode_view_tree")
    util.remove_view(cr, "mail.mail_shortcode_view_form")

    # Set unpin_dt to now for all non-pinned members
    util.create_column(cr, "discuss_channel_member", "unpin_dt", "timestamp")
    util.explode_execute(
        cr,
        """
            UPDATE discuss_channel_member
               SET unpin_dt = NOW() AT TIME ZONE 'UTC'
             WHERE is_pinned IS NOT TRUE
        """,
        table="discuss_channel_member",
    )
    util.remove_column(cr, "discuss_channel_member", "is_pinned")
