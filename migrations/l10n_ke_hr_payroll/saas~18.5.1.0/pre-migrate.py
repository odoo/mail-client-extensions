from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_version", "l10n_ke_tier_2_remit", "varchar", default="nssf")
    util.create_column(cr, "hr_version", "l10n_ke_pension_remit", "varchar", default="nssf")
    util.hr_payroll.remove_salary_rule(cr, "l10n_ke_hr_payroll.l10n_ke_employees_salary_pension_contribution")
