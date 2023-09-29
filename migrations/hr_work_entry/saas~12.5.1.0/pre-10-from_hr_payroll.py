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

    util.rename_xmlid(cr, *eb("hr_work_entry.hr_work_entry_{,view_}tree"))
    util.rename_xmlid(cr, *eb("hr_work_entry.{view_hr_work_entry_filter,hr_work_entry_view_search}"))
    util.rename_xmlid(cr, *eb("hr_work_entry.hr_work_entry_{,view_}form"))
    util.rename_xmlid(cr, *eb("hr_work_entry.hr_work_entry_type_{,view_}tree"))

    if util.table_exists(cr, "hr_work_entry"):
        util.create_column(cr, "hr_work_entry", "conflict", "boolean")  # Always false, state 'conflict' is new
        cr.execute("UPDATE hr_work_entry SET state='draft' WHERE state='confirmed'")

        util.remove_constraint(cr, "hr_work_entry", "hr_work_entry__unique")
