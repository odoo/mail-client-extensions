# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'account_analytic_account', 'active', 'boolean')
    cr.execute("""
        UPDATE account_analytic_account
           SET active = (coalesce(account_type, 'normal') = 'normal')
    """)
    util.delete_model(cr, 'account.analytic.chart')
