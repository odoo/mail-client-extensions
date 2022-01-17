# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    util.remove_view(cr, "l10n_be_hr_payroll.hr_employee_view_form")
    util.remove_view(cr, "l10n_be_hr_payroll.hr_payroll_report_view_search")
    util.remove_view(cr, "l10n_be_hr_payroll.hr_payslip_view_form_inherit_december")
    util.remove_view(cr, "l10n_be_hr_payroll.l10n_be_group_insurance_wizard_view_form")
    util.remove_view(cr, "l10n_be_hr_payroll.l10n_be_december_slip_wizard_view_form")
    util.remove_view(cr, "l10n_be_hr_payroll.dmfa_xml_report_insurance_group")
    util.remove_view(cr, "l10n_be_hr_payroll.l10n_be_individual_account_wizard_view_form")

    # Split l10n_be_hr_payroll_canteen into l10n_be_hr_payroll/l10n_be_hr_contract_salary
    util.move_field_to_module(
        cr, "hr.contract", "l10n_be_canteen_cost", "l10n_be_hr_contract_salary", "l10n_be_hr_payroll"
    )

    util.remove_model(cr, "l10n_be.individual.account.wizard")

    for model in ["281_10", "281_45"]:
        util.remove_field(cr, f"l10n_be.{model}", "pdf_filename")
        util.remove_field(cr, f"l10n_be.{model}", "pdf_file")
        util.move_field_to_module(
            cr, f"l10n_be.{model}", "documents_enabled", "l10n_be_hr_payroll", "documents_l10n_be_hr_payroll"
        )
