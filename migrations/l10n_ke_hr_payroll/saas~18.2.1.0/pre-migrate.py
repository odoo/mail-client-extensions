from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "l10n.ke.hr.payroll.nhif.report.line.wizard")
    util.remove_model(cr, "l10n.ke.hr.payroll.nhif.report.wizard")

    scripts = util.import_script("l10n_ke_hr_payroll/0.0.0/pre-migrate.py")
    scripts.remove_salary_rule(cr, "l10n_ke_hr_payroll.l10n_ke_employees_salary_shif_amount_hidden")
    scripts.remove_salary_rule(cr, "l10n_ke_hr_payroll.l10n_ke_employees_shif_relief")
