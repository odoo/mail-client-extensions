# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_attendance.hr_attendance_view_graph")
    util.remove_view(cr, "hr_attendance.hr_attendance_view_pivot")

    util.create_column(cr, "res_company", "hr_attendance_overtime", "bool")
    util.create_column(cr, "res_company", "overtime_start_date", "date")
    util.create_column(cr, "res_company", "overtime_company_threshold", "int")
    util.create_column(cr, "res_company", "overtime_employee_threshold", "int")

    # The following fields have been moved from hr.employee.base to hr.employee
    for field in [
        "attendance_ids",
        "last_attendance_id",
        "last_check_in",
        "last_check_out",
        "attendance_state",
        "hours_last_month",
        "hours_today",
        "hours_last_month_display",
    ]:
        util.remove_field(cr, "hr.employee.base", field, drop_column=False, skip_inherit=("hr.employee",))
