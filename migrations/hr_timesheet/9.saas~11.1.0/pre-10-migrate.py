# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'account_analytic_line', 'department_id', 'int4')
    cr.execute("""
        UPDATE account_analytic_line l
           SET department_id = e.department_id
          FROM hr_employee e, resource_resource r
         WHERE e.resource_id = r.id
           AND r.user_id = l.user_id
    """)

    act = util.ref(cr, 'hr_timesheet.act_hr_timesheet_line')
    if act:
        cr.execute("""
            UPDATE ir_act_window
               SET domain='[]', context='{}', view_id=NULL
             WHERE id=%s
        """, [act])
        cr.execute("DELETE FROM ir_act_window_view WHERE act_window_id=%s", [act])

    util.delete_model(cr, 'hr.timesheet.report')
