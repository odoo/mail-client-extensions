# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'gamification_challenge', 'user_domain', 'varchar')
    cr.execute("""UPDATE gamification_challenge
                     SET user_domain='[("groups_id", "=", ' || autojoin_group_id::varchar || ')]'
                   WHERE autojoin_group_id IS NOT NULL
               """)
