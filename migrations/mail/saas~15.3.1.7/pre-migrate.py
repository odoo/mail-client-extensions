# -*- coding: utf-8 -*-

from odoo.upgrade.util.records import _remove_records


def migrate(cr, version):

    # Remove the <mail.channel> whose 'channel_type' is null
    cr.execute(
        """
            SELECT id
              FROM mail_channel
             WHERE channel_type IS NULL
        """
    )
    _remove_records(cr, "mail.channel", [cid for cid, in cr.fetchall()])
