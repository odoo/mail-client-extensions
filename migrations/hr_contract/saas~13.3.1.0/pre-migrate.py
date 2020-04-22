# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    fields = {
        "hr.contract": ["structure_type_id", "company_country_id"],
        "hr.payroll.structure.type": ["name", "default_resource_calendar_id", "country_id"],
    }
    for model in fields:
        for field in fields[model]:
            util.move_field_to_module(cr, model, field, "hr_payroll", "hr_contract")

    util.remove_field(cr, "hr.contract", "advantages")

    util.rename_xmlid(cr, *eb("hr_{payroll,contract}.access_hr_payroll_structure_type_hr_contract_manager"))
    util.rename_xmlid(cr, *eb("hr_{payroll,contract}.ir_rule_hr_payroll_structure_type_multi_company"))
    util.rename_xmlid(cr, *eb("{l10n_be_hr_payroll,hr_contract}.structure_type_employee_cp200"))
