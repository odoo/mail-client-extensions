# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("{hr_payroll,hr_work_entry_contract}.hr_work_entry_regeneration_wizard"))
    util.rename_xmlid(cr, *eb("{hr_payroll,hr_work_entry_contract}.hr_work_entry_regeneration_wizard_action"))
    util.move_model(cr, "hr.work.entry.regeneration.wizard", "hr_payroll", "hr_work_entry_contract")
    util.remove_view(cr, "hr_work_entry_contract.hr_contract_view_form_inherit")
    util.remove_view(cr, "hr_work_entry_contract.resource_calendar_view_form_inherit")
