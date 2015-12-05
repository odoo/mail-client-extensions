# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'account_analytic_line', 'task_id', 'int4')
    if util.table_exists(cr, 'hr_analytic_timesheet'):
      cr.execute("""
          UPDATE account_analytic_line l
             SET task_id=w.task_id
            FROM hr_analytic_timesheet h,
                 project_task_work w
           WHERE l.id = h.line_id
             AND h.id = w.hr_analytic_timesheet_id
      """)

    util.delete_model(cr, 'project.task.work')
