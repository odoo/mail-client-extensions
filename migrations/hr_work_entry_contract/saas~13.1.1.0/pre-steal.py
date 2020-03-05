# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    for wet in {
        "leave",
        "compensatory",
        "home_working",
        "unpaid_leave",
        "sick_leave",
        "legal_leave",
        # demo data
        "extra_hours",
        "long_leave",
    }:
        util.rename_xmlid(cr, *eb(f"hr_{{payroll,work_entry_contract}}.work_entry_type_{wet}"))

    renames = util.splitlines(
        """
        ir_rule_hr_work_entry_multi_company

        # menus
        menu_hr_payroll_root
        menu_work_entry
        menu_work_entry_conflicts
        menu_hr_work_entry_confirguration  # with the typo
        menu_hr_work_entry_type_view

        # views
        hr_work_entry_action_view_gantt
        hr_work_entry_action_conflict_view_gantt
        hr_work_entry_gantt
    """
    )
    for xid in renames:
        util.rename_xmlid(cr, *eb(f"hr_{{payroll,work_entry_contract}}.{xid}"))

    util.rename_xmlid(
        cr,
        "hr_payroll.payroll_hr_work_entry_view_calendar_inherit",
        "hr_work_entry_contract.hr_work_entry_contract_view_calendar_inherit",
    )

    util.move_field_to_module(cr, "hr.contract", "date_generated_from", "hr_payroll", "hr_work_entry_contract")
    util.move_field_to_module(cr, "hr.contract", "date_generated_to", "hr_payroll", "hr_work_entry_contract")

    util.move_field_to_module(cr, "hr.work.entry", "contract_id", "hr_payroll", "hr_work_entry_contract")
    util.move_field_to_module(cr, "hr.work.entry", "employee_id", "hr_payroll", "hr_work_entry_contract")

    util.move_field_to_module(cr, "hr.work.entry.type", "is_leave", "hr_payroll", "hr_work_entry_contract")
