# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "hr_holidays.hr_leave_rule_employee_unlink")
    util.remove_field_metadata(cr, "hr.employee.base", "current_leave_id")
    util.remove_field(cr, "hr.employee.public", "current_leave_id")
