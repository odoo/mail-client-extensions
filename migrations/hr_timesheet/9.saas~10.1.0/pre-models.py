# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'account_analytic_line', 'project_id', 'int4')

    cr.execute("""
        UPDATE account_analytic_line l
           SET project_id = p.id
          FROM project_project p
         WHERE p.analytic_account_id = l.account_id
           AND l.is_timesheet
    """)
