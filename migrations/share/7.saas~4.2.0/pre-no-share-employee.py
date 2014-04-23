# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    gid = util.ref(cr, 'base.group_user')
    cr.execute("""UPDATE res_users u
                     SET share = NOT EXISTS(SELECT 1
                                              FROM res_groups_users_rel
                                             WHERE gid = %s
                                               AND uid = u.id)
                """, (gid,))
