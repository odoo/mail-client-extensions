# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'hr_employee', 'last_attendance_id', 'int4')

    cr.execute("""
        WITH lastatt AS (
            SELECT employee_id,
                   (array_agg(id ORDER BY check_in desc))[1] as id
              FROM hr_attendance
            GROUP BY employee_id
        )
        UPDATE hr_employee e
           SET last_attendance_id = l.id
          FROM lastatt l
         WHERE l.employee_id = e.id
    """)
