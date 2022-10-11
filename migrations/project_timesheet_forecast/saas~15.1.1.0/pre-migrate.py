# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "planning_slot", "allocated_hours_cost", "float8", default=0.0)
    util.create_column(cr, "planning_slot", "effective_hours_cost", "float8", default=0.0)

    field_name = "hourly_cost" if util.version_gte("16.0") else "timesheet_cost"
    cr.execute(
        f"""
        UPDATE planning_slot s
        SET allocated_hours_cost = COALESCE(s.allocated_hours, 0.0) * e.{field_name},
            effective_hours_cost = COALESCE(s.effective_hours, 0.0) * e.{field_name}
        FROM hr_employee e
        WHERE e.id = s.employee_id
        AND e.{field_name} IS NOT NULL
    """
    )
