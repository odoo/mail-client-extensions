# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # recompute badge image_{small,medium}
    if not util.version_gte('saas~12.5'):
        Badge = util.env(cr)['gamification.badge']
        ids = Badge.search([('image', '!=', False)]).ids
        for badge in util.iter_browse(Badge, ids):
            badge.image = badge.image

    # recompute karma rank
    if not util.column_exists(cr, "res_users", "_karma"):
        return

    util.remove_column(cr, "res_users", "karma")
    cr.execute("ALTER TABLE res_users RENAME COLUMN _karma TO karma")

    cr.execute("""
        WITH ranks AS (
            SELECT id, karma_min, LEAD(id) OVER (ORDER BY karma_min) next_rank
              FROM gamification_karma_rank
        ),
        user_ranks AS (
            SELECT u.id,
                   (array_agg(r.id ORDER BY r.karma_min DESC))[1] rank_id,
                   (array_agg(r.next_rank ORDER BY r.karma_min DESC))[1] next_rank_id
              FROM res_users u, ranks r
             WHERE u.karma >= r.karma_min
          GROUP BY u.id
        )
        UPDATE res_users u
           SET rank_id = r.rank_id,
               next_rank_id = r.next_rank_id
          FROM user_ranks r
         WHERE r.id = u.id
    """)
