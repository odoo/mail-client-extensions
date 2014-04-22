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

    cr.execute("""UPDATE res_users u
                     SET share = NOT EXISTS(SELECT 1
                                              FROM res_groups_users_rel
                                             WHERE gid=(SELECT res_id
                                                          FROM ir_model_data
                                                         WHERE module=%s
                                                           AND name=%s)
                                               AND uid = u.id)
                """, ('base', 'group_user'))
