# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, 'pos_order', 'employee_id', 'int4')
    util.create_column(cr, 'pos_order', 'cashier', 'varchar')
    cr.execute("""
        UPDATE pos_order o
           SET o.cashier=u.name
          FROM res_users u
         WHERE o.user_id=u.id
    """)
