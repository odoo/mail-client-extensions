# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    group_multi_warehouse = util.ref(cr, 'stock.group_stock_multi_warehouses')
    group_multi_locations = util.ref(cr, 'stock.group_stock_multi_locations')

    cr.execute("""
        INSERT INTO res_groups_users_rel(gid, uid)
             SELECT %s, uid
               FROM res_groups_users_rel
              WHERE gid = %s
    """, [group_multi_warehouse, group_multi_locations])
