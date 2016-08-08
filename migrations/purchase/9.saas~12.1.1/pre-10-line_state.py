# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'purchase_order_line', 'state', 'varchar')
    cr.execute("""
        UPDATE purchase_order_line l
           SET state = o.state
          FROM purchase_order o
         WHERE o.id = l.order_id
    """)
