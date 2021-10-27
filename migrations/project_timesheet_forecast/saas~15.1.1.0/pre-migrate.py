# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "planning_slot", "allocated_hours_cost", "float8", default=0.0)
    util.create_column(cr, "planning_slot", "effective_hours_cost", "float8", default=0.0)

    cr.execute(
        """
        UPDATE planning_slot s
           SET allocated_hours_cost = COALESCE(s.allocated_hours, 0.0) * e.timesheet_cost,
               effective_hours_cost = COALESCE(s.effective_hours, 0.0) * e.timesheet_cost
          FROM hr_employee e
         WHERE e.id = s.employee_id
           AND e.timesheet_cost IS NOT NULL
    """
    )
