# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'hr_contract', 'department_id', 'int4')
    cr.execute("""UPDATE hr_contract c
                     SET department_id=e.department_id
                    FROM hr_employee e
                   WHERE e.id = c.employee_id
               """)
    util.create_column(cr, 'hr_contract', 'state', 'varchar')
    # current contract are running
    cr.execute("UPDATE hr_contract SET state='open'")
