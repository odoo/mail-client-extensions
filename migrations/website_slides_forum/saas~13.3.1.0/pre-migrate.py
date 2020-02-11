# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "forum_forum", "slide_channel_id", "int4")

    # slide_channel_id is now a computed stored field.
    # Privacy must be set to '' if slide_channel as this forum follow the slide_channel privacy

    cr.execute(
        """
            UPDATE forum_forum f
               SET slide_channel_id = c.id,
                   privacy = NULL
              FROM slide_channel c
             WHERE c.forum_id = f.id
        """
    )
