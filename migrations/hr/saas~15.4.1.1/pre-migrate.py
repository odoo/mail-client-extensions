# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.plan.wizard", "employee_id")
    util.create_m2m(
        cr, "hr_employee_hr_plan_wizard_rel", "hr_employee", "hr_plan_wizard", "employee_id", "plan_wizard_id"
    )
