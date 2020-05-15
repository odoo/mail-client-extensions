# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces

    util.move_model(cr, "hr.work.entry", "hr_payroll", "hr_work_entry")
    util.move_model(cr, "hr.work.entry.type", "hr_payroll", "hr_work_entry")
    util.move_model(cr, "hr.user.work.entry.employee", "hr_payroll", "hr_work_entry")

    util.remove_field(cr, "hr.work.entry", "display_warning")

    util.move_field_to_module(cr, "resource.calendar.attendance", "work_entry_type_id", "hr_payroll", "hr_work_entry")
    util.move_field_to_module(cr, "resource.calendar.leaves", "work_entry_type_id", "hr_payroll", "hr_work_entry")

    util.move_field_to_module(cr, "hr.work.entry", "contract_id", "hr_work_entry", "hr_payroll")
    util.move_field_to_module(cr, "hr.work.entry", "leave_id", "hr_work_entry", "hr_payroll")
    util.move_field_to_module(cr, "hr.work.entry.type", "is_unforeseen", "hr_work_entry", "hr_payroll")
    util.move_field_to_module(cr, "hr.work.entry.type", "is_leave", "hr_work_entry", "hr_payroll")
    util.move_field_to_module(cr, "hr.work.entry.type", "leave_type_ids", "hr_work_entry", "hr_payroll")

    util.rename_xmlid(cr, *eb("hr_{payroll,work_entry}.hr_user_work_entry_employee"))
    util.rename_xmlid(cr, *eb("hr_{payroll,work_entry}.hr_work_entry_action"))
    util.rename_xmlid(cr, *eb("hr_{payroll,work_entry}.hr_work_entry_action_conflict"))
    util.rename_xmlid(cr, *eb("hr_{payroll.hr_work_entry_tree,work_entry.hr_work_entry_view_tree}"))
    util.rename_xmlid(cr, *eb("hr_{payroll.view_hr_work_entry_filter,work_entry.hr_work_entry_view_search}"))
    util.rename_xmlid(cr, *eb("hr_{payroll.hr_work_entry_form,work_entry.hr_work_entry_view_form}"))
    util.rename_xmlid(cr, *eb("hr_{payroll.hr_work_entry_type_tree,work_entry.hr_work_entry_type_view_tree}"))
    util.rename_xmlid(cr, *eb("hr_{payroll,work_entry}.hr_work_entry_type_view_form"))
    util.rename_xmlid(cr, *eb("hr_{payroll,work_entry}.hr_work_entry_type_view_kanban"))
    util.rename_xmlid(cr, *eb("hr_{payroll,work_entry}.work_entry_type_attendance"))

    if util.table_exists(cr, "hr_work_entry"):
        util.create_column(cr, "hr_work_entry", "conflict", "boolean")  # Always false, state 'conflict' is new
        cr.execute("UPDATE hr_work_entry SET state='draft' WHERE state='confirmed'")

        cr.execute("ALTER TABLE hr_work_entry DROP CONSTRAINT hr_work_entry__unique")
        cr.execute("DELETE FROM ir_model_constraint WHERE name = 'hr_work_entry__unique'")
