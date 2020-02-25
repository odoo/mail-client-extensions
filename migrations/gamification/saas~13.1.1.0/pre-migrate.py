# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "gamification.badge", "stat_count", "granted_count")
    util.rename_field(cr, "gamification.badge", "stat_count_distinct", "granted_users_count")

    util.rename_field(cr, "gamification.challenge", "category", "challenge_category")

    cr.execute(
        """
        UPDATE gamification_karma_rank
           SET karma_min = 1
         WHERE COALESCE(karma_min, 0) < 1
    """
    )
