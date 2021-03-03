# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        INSERT INTO website_visitor_push_subscription(
            website_visitor_id, push_token
        )
        SELECT id, push_token
          FROM website_visitor
         WHERE has_push_notifications = TRUE
    """
    )
    util.remove_field(cr, "website.visitor", "push_token")
