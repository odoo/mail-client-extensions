# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'account_analytic_line', 'issue_id', 'int4')
    cr.execute("""
        UPDATE account_analytic_line l
           SET issue_id=h.issue_id
          FROM hr_analytic_timesheet h
         WHERE l.id = h.line_id
    """)
