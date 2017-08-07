# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'account_analytic_line', 'employee_id', 'int4')
    cr.execute("""
        WITH user_resources AS (
            SELECT (array_agg(id ORDER BY name))[1] as id, user_id
              FROM resource_resource
             WHERE resource_type = 'user'
               AND user_id IS NOT NULL
          GROUP BY user_id
        )
        UPDATE account_analytic_line l
           SET employee_id = e.id
          FROM user_resources r JOIN hr_employee e ON (r.id = e.resource_id)
         WHERE r.user_id = l.user_id
    """)

    gid = util.ref(cr, 'hr_timesheet.group_hr_timesheet_user')
    # Now in noupdate=1 => manual update
    if gid:
        cr.execute("UPDATE res_groups SET name='User' WHERE id=%s", [gid])
        cr.execute("""
            DELETE FROM ir_translation
             WHERE type='model'
               AND name='res.groups,name'
               AND res_id=%s
        """, [gid])
