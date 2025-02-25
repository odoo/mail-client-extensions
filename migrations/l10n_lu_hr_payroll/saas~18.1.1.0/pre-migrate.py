from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "l10n_lu_hr_payroll.hr_payroll_dashboard_warning_no_tax_classification")
    util.delete_unused(cr, "l10n_lu_hr_payroll.work_entry_type_wage_supplement_70", deactivate=True)
    util.delete_unused(cr, "l10n_lu_hr_payroll.hr_salary_rule_category_ded_net")
