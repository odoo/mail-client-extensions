# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'sale_order', 'subscription_management', 'varchar')
    cr.execute("""
        UPDATE sale_order
           SET subscription_management = CASE WHEN update_contract THEN 'renew'
                                              WHEN project_id IS NOT NULL THEN 'upsell'
                                              ELSE 'create'
                                          END
    """)
