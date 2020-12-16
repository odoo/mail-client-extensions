# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("{hr_payroll,hr_work_entry_contract}.hr_work_entry_regeneration_wizard"))
    util.rename_xmlid(cr, *eb("{hr_payroll,hr_work_entry_contract}.hr_work_entry_regeneration_wizard_action"))
    util.move_model(cr, "hr.work.entry.regeneration.wizard", "hr_payroll", "hr_work_entry_contract")

    util.remove_view(cr, "hr_work_entry_contract.hr_contract_view_form_inherit")

    view_id = util.rename_xmlid(
        cr,
        "hr_work_entry_contract.resource_calendar_view_form_inherit",
        "hr_work_entry_contract.resource_calendar_view_form",
    )
    if view_id:
        cr.execute(
            "DELETE FROM ir_ui_view_group_rel WHERE view_id = %s AND group_id = %s",
            [view_id, util.ref(cr, "hr_payroll.group_hr_payroll_user")],
        )
