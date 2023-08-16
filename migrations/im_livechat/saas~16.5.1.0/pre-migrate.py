from odoo.upgrade import util


def migrate(cr, version):
    util.explode_execute(
        cr,
        """
        UPDATE discuss_channel
           SET livechat_active = false
         WHERE livechat_active IS NOT false
        """,
        table="discuss_channel",
    )
    util.explode_execute(
        cr,
        """
        UPDATE discuss_channel_member m
           SET is_pinned = false
          FROM discuss_channel c
         WHERE c.id = m.channel_id
           AND c.channel_type = 'livechat'
           AND m.is_pinned IS NOT false
        """,
        table="discuss_channel_member",
        alias="m",
    )
