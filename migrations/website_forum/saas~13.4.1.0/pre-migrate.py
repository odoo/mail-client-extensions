# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "forum_forum", "teaser", "text")
    cr.execute(
        r"""
            UPDATE forum_forum
               SET teaser = CASE WHEN length(description) > 180
                                 THEN concat(left(replace(description, E'\n', ' '), 180), '...')
                                 ELSE description
                             END
        """
    )

    cr.execute(
        """
        UPDATE forum_post_reason
           SET reason_type = 'basic'
         WHERE reason_type NOT IN ('basic', 'offensive')
    """
    )

    util.create_column(cr, "website", "forums_count", "int4")
    cr.execute(
        """
        UPDATE website w
           SET forums_count = (
              SELECT count(*)
                FROM forum_forum f
               WHERE f.active
                 AND (f.website_id is NULL OR f.website_id = w.id)
            )
    """
    )
