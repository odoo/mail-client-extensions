from odoo.upgrade import util
from odoo.upgrade.util.hr_payroll import remove_salary_rule


def migrate(cr, version):
    util.remove_view(cr, "l10n_sa_hr_payroll.hr_payslip_run_view_form")
    util.remove_view(cr, "l10n_sa_hr_payroll.hr_leave_type_view_form")

    util.update_record_from_xml(cr, "l10n_sa_hr_payroll.ksa_saudi_employee_payroll_structure")
    util.remove_field(cr, "hr.employee", "l10n_sa_leaves_count_compensable")
    util.remove_field(cr, "hr.leave.type", "l10n_sa_is_compensable")

    remove_salary_rule(cr, "l10n_sa_hr_payroll.ksa_saudi_annual_leave_compensation_salary_rule")
    util.delete_unused(cr, "l10n_sa_hr_payroll.ksa_expat_employee_payroll_structure")
