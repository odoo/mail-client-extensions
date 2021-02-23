# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("hr_work_entry_contract{,_enterprise}.hr_work_entry_action_conflict_view_gantt"))
    util.rename_xmlid(cr, *eb("hr_work_entry_contract{,_enterprise}.hr_work_entry_action_view_gantt"))
    util.rename_xmlid(cr, *eb("hr_work_entry_contract{,_enterprise}.hr_work_entry_gantt"))

    util.rename_xmlid(cr, *eb("hr_work_entry_contract{,_enterprise}.menu_hr_payroll_root"))
    util.rename_xmlid(cr, *eb("hr_work_entry_contract{,_enterprise}.menu_hr_payroll_work_entries_root"))
    util.rename_xmlid(cr, *eb("hr_work_entry_contract{,_enterprise}.menu_hr_payroll_configuration"))
    util.rename_xmlid(cr, *eb("hr_work_entry_contract{,_enterprise}.menu_work_entry"))
    util.rename_xmlid(cr, *eb("hr_work_entry_contract{,_enterprise}.menu_work_entry_conflicts"))
    util.rename_xmlid(
        cr,
        "hr_work_entry_contract.menu_hr_work_entry_confirguration",
        "hr_work_entry_contract_enterprise.menu_hr_work_entry_configuration",
    )
    util.rename_xmlid(cr, *eb("hr_work_entry_contract{,_enterprise}.menu_hr_work_entry_type_view"))
    util.rename_xmlid(cr, *eb("hr_work_entry_contract{,_enterprise}.menu_resource_calendar_view"))
    util.rename_xmlid(cr, *eb("hr_work_entry_contract{,_enterprise}.hr_menu_contract"))
