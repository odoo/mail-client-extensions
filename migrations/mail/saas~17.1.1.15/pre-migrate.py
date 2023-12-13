# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
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
