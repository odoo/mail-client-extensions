from odoo.addons.base.maintenance.migrations.util.hr_payroll import remove_salary_rule


def migrate(cr, version):
    remove_salary_rule(cr, "l10n_eg_hr_payroll.egypt_social_insurance_contribution_total")
