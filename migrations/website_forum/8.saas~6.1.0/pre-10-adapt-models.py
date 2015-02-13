# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'forum_post', 'relevancy', 'float8')
    # precompute value in SQL
    cr.execute("""UPDATE forum_post p
                     SET relevancy=CASE WHEN create_date IS NOT NULL THEN
                            sign(vote_count) * (abs(vote_count - 1) ^ 0.8
                            / ((extract(epoch from now() at time zone 'utc'
                                - create_date)/86400)::int + 2) ^ 1.8)
                          ELSE 0 END
               """)

    util.create_column(cr, 'forum_post_vote', 'forum_id', 'int4')
    util.create_column(cr, 'forum_post_vote', 'recipient_id', 'int4')
    cr.execute("""UPDATE forum_post_vote v
                     SET forum_id=p.forum_id, recipient_id=p.create_uid
                    FROM forum_post p
                   WHERE p.id = v.post_id
               """)

    # create columns ourself to not let the ORM assign default values for existing records
    util.create_column(cr, 'forum_forum', 'allow_link', 'boolean')
    util.create_column(cr, 'forum_forum', 'allow_discussion', 'boolean')
