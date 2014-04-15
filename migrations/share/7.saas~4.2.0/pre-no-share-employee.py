# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # remove "employee" group from share users
    cr.execute("""DELETE FROM res_groups_users_rel
                        WHERE gid=(SELECT res_id
                                     FROM ir_model_data
                                    WHERE module=%s
                                      AND name=%s)
                          AND uid IN (SELECT id
                                        FROM res_users
                                       WHERE share=%s)
                """, ('base', 'group_user', True))

    # `share` is now a function field. force recomputation
    util.remove_column(cr, 'res_users', 'share')
