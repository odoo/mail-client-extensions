from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "hr.payroll.generate.warrant.payslips")
    util.remove_model(cr, "hr.payroll.generate.warrant.payslips.line")
    util.remove_view(cr, "l10n_be_hr_payroll.hr_payslip_run_view_tree")
    util.move_field_to_module(
        cr, "hr.contract", "l10n_be_mobility_budget", "l10n_be_hr_contract_salary", "l10n_be_hr_payroll"
    )
    util.move_field_to_module(
        cr, "hr.contract", "l10n_be_mobility_budget_amount", "l10n_be_hr_contract_salary", "l10n_be_hr_payroll"
    )
    util.move_field_to_module(
        cr, "hr.contract", "l10n_be_mobility_budget_amount_monthly", "l10n_be_hr_contract_salary", "l10n_be_hr_payroll"
    )
    util.move_field_to_module(
        cr, "hr.contract", "l10n_be_wage_with_mobility_budget", "l10n_be_hr_contract_salary", "l10n_be_hr_payroll"
    )
