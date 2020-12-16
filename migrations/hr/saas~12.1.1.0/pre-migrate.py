# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.move_field_to_module(cr, "hr.employee", "barcode", "hr_attendance", "hr")
    util.move_field_to_module(cr, "hr.employee", "pin", "hr_attendance", "hr")
    util.rename_xmlid(cr, "hr_attendance.print_employee_badge", "hr.print_employee_badge")
    util.rename_xmlid(cr, "hr_attendance.hr_employee_print_badge", "hr.hr_employee_print_badge")
