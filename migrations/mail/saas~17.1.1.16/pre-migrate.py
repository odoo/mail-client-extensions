from odoo.upgrade import util


def migrate(cr, version):
    util.explode_execute(
        cr,
        """
            UPDATE discuss_channel_member
               SET fold_state = 'closed'
              FROM discuss_channel
             WHERE discuss_channel_member.channel_id = discuss_channel.id
               AND discuss_channel.channel_type NOT IN ('channel', 'group')
               AND discuss_channel_member.is_pinned IS NOT true
        """,
        table="discuss_channel_member",
    )

    util.explode_execute(
        cr,
        """
            UPDATE discuss_channel_member
               SET fold_state = 'closed'
             WHERE is_minimized IS NOT true
        """,
        table="discuss_channel_member",
    )
    util.remove_field(cr, "discuss.channel.member", "is_minimized")

    # web push naming cleaning
    util.rename_model(cr, "mail.notification.web.push", "mail.push")
    util.rename_model(cr, "mail.partner.device", "mail.push.device")
    util.rename_field(cr, "mail.push", "user_device", "mail_push_device_id")
    util.rename_xmlid(cr, "mail.access_mail_partner_device", "mail.access_mail_push_device_system")
    util.rename_xmlid(cr, "mail.access_mail_notification_web_push", "mail.access_mail_push_system")
