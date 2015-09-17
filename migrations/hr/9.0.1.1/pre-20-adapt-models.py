# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # no more hierarchy on employee categories
    cr.execute("""
        WITH RECURSIVE cats AS (
            SELECT id, name
              FROM hr_employee_category
             WHERE parent_id IS NULL
             UNION
            SELECT c.id, concat(w.name, ' / ', c.name)
              FROM hr_employee_category c
              JOIN cats w ON (c.parent_id = w.id)
        )
        UPDATE hr_employee_category c
           SET name = w.name
          FROM cats w
         WHERE c.id = w.id
    """)

    util.remove_field(cr, 'hr.employee.category', 'parent_id')

    util.delete_model(cr, 'hr.config.settings')
