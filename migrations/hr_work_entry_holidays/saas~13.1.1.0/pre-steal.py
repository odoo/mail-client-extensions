# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    util.move_field_to_module(cr, "hr.leave.type", "work_entry_type_id", "hr_payroll", "hr_work_entry_holidays")

    util.move_field_to_module(cr, "hr.work.entry", "leave_id", "hr_payroll", "hr_work_entry_holidays")
    util.move_field_to_module(cr, "hr.work.entry", "leave_state", "hr_payroll", "hr_work_entry_holidays")

    util.move_field_to_module(cr, "hr.work.entry.type", "leave_type_ids", "hr_payroll", "hr_work_entry_holidays")

    util.rename_xmlid(cr, *eb("hr_{payroll,work_entry_holidays}.payroll_hr_work_entry_view_form_inherit"))
    util.rename_xmlid(cr, *eb("hr_{payroll,work_entry_holidays}.work_entry_type_leave_form_inherit"))
