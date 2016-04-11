# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    lmc = util.ref(cr, 'base.group_light_multi_company')
    mc = util.ref(cr, 'base.group_multi_company')
    cr.execute("""
        INSERT INTO res_groups_users_rel(uid, gid)
             SELECT uid, %s
               FROM res_groups_users_rel
              WHERE gid = %s
             EXCEPT
             SELECT uid, gid
               FROM res_groups_users_rel
              WHERE gid = %s
    """, [mc, lmc, mc])
