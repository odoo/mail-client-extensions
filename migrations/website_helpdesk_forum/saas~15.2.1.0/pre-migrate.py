# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_helpdesk_forum.website_helpdesk_forum_team_page")
    util.remove_field(cr, "helpdesk.team", "forum_id")
    util.remove_field(cr, "helpdesk.team", "forum_url")

    util.create_column(cr, "forum_post", "ticket_id", "int4")
    util.create_m2m(cr, "forum_post_helpdesk_ticket_rel", "helpdesk_ticket", "forum_post")

    cr.execute(
        """
        INSERT INTO forum_post_helpdesk_ticket_rel
             SELECT id, forum_post_id
               FROM helpdesk_ticket
              WHERE forum_post_id IS NOT NULL
        """
    )

    cr.execute(
        """
        UPDATE forum_post
           SET ticket_id = ht.id
          FROM helpdesk_ticket ht
         WHERE ht.forum_post_id = forum_post.id
        """
    )

    util.update_field_usage(cr, "helpdesk.ticket", "forum_post_id", "forum_post_ids")
    util.remove_field(cr, "helpdesk.ticket", "forum_post_id")
