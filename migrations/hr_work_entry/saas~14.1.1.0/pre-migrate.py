# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_work_entry", "department_id", "int4")
    cr.execute(
        """UPDATE hr_work_entry
           SET department_id=hr_employee.department_id
           FROM hr_employee
           WHERE hr_work_entry.employee_id = hr_employee.id"""
    )
