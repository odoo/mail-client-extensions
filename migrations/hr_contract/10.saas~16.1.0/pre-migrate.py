# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'hr.contract', 'trial_date_start')
    util.create_column(cr, 'hr_contract', 'company_id', 'int4')
    cr.execute("""
        UPDATE hr_contract c
           SET company_id = r.company_id
          FROM hr_employee e
          JOIN resource_resource r ON (e.resource_id = r.id)
         WHERE e.id = c.employee_id
    """)
