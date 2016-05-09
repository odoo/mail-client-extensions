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

    # use the project of the task/issue if set
    cr.execute("""
        UPDATE account_analytic_line l
           SET project_id = t.project_id
          FROM project_task t
         WHERE t.id = l.task_id
           AND l.project_id IS NULL
           AND l.is_timesheet
    """)

    if util.column_exists(cr, 'account_analytic_line', 'issue_id') and util.table_exists(cr, 'project_issue'):
        cr.execute("""
            UPDATE account_analytic_line l
               SET project_id = i.project_id
              FROM project_issue i
             WHERE i.id = l.issue_id
               AND l.project_id IS NULL
               AND l.is_timesheet
        """)
