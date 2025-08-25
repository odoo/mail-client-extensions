from odoo.upgrade import util
from odoo.upgrade.util.hr_payroll import remove_salary_rule


def migrate(cr, version):
    util.remove_field(cr, "hr.version", "l10n_mx_schedule_pay")
    util.remove_field(cr, "hr.payroll.structure.type", "l10n_mx_default_schedule_pay")
    util.remove_field(cr, "hr.payroll.structure", "l10n_mx_default_schedule_pay")
    util.remove_field(cr, "hr.payroll.structure", "l10n_mx_schedule_pay")
    util.remove_field(cr, "hr.payroll.structure", "country_code")
    util.remove_view(cr, "l10n_mx_hr_payroll.hr_payroll_structure_type_view_form")
    util.remove_view(cr, "l10n_mx_hr_payroll.hr_payroll_structure_view_form")

    util.remove_field(cr, "hr.version", "l10n_mx_external_annual_declaration")
    util.remove_field(cr, "hr.employee", "l10n_mx_external_annual_declaration")
    remove_salary_rule(cr, "l10n_mx_hr_payroll.l10n_mx_employees_salary_subsidy_adjustment")
