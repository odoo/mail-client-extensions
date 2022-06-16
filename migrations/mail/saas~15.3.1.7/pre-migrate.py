# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    # Remove the <mail.channel> whose 'channel_type' is null
    cr.execute(
        """
            SELECT id
              FROM mail_channel
             WHERE channel_type IS NULL
        """
    )
    util.remove_records(cr, "mail.channel", [cid for cid, in cr.fetchall()])
