from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("l10n_in_hr_payroll.{,l10n_in_}hr_payslip_rule_dla"))
    util.rename_xmlid(cr, *eb("l10n_in_hr_payroll.{,l10n_in_}hr_payslip_rule_employer_esics"))
    util.rename_xmlid(cr, *eb("l10n_in_hr_payroll.{,l10n_in_}hr_payslip_rule_expense"))
    util.rename_xmlid(cr, *eb("l10n_in_hr_payroll.{,l10n_in_}hr_payslip_rule_gratuity"))
    util.rename_xmlid(cr, *eb("l10n_in_hr_payroll.{,l10n_in_}hr_payslip_rule_tds"))
    util.rename_xmlid(
        cr,
        *eb(
            "l10n_in_hr_payroll.{l10n_in_hr_salary_rule_attach_salary,l10n_in_hr_payroll_structure_in_employee_salary_attachment_of_salary_rule}"
        ),
    )
    util.rename_xmlid(
        cr,
        *eb(
            "l10n_in_hr_payroll.{l10n_in_hr_salary_rule_assig_salary,l10n_in_hr_payroll_structure_in_employee_salary_assignment_of_salary_rule}"
        ),
    )
