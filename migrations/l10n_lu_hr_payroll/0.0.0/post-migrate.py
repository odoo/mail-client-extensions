from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Being a post script, the records have been updated and don't reference the categories to be removed.
    # This way, the util doesn't unnecesarily detect them as 'used' and can delete them.
    if util.version_between("16.0", "18.0"):
        util.delete_unused(cr, "l10n_lu_hr_payroll.l10n_lu_employees_taxes_total")
        util.delete_unused(cr, "l10n_lu_hr_payroll.hr_salary_rule_category_bik_transport")
        util.delete_unused(cr, "l10n_lu_hr_payroll.hr_salary_rule_category_gross_tmp")
        util.delete_unused(cr, "l10n_lu_hr_payroll.hr_salary_rule_category_taxes_data")
        util.delete_unused(cr, "l10n_lu_hr_payroll.hr_salary_rule_category_total_allowance")
