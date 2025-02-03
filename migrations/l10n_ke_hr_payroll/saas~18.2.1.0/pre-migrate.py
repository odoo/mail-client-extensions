from odoo.upgrade import util
from odoo.upgrade.util.hr_payroll import remove_salary_rule


def migrate(cr, version):
    util.remove_model(cr, "l10n.ke.hr.payroll.nhif.report.line.wizard")
    util.remove_model(cr, "l10n.ke.hr.payroll.nhif.report.wizard")

    remove_salary_rule(cr, "l10n_ke_hr_payroll.l10n_ke_employees_salary_shif_amount_hidden")
    remove_salary_rule(cr, "l10n_ke_hr_payroll.l10n_ke_employees_shif_relief")

    util.remove_record(cr, "l10n_ke_hr_payroll.rule_parameter_shif_min_basic_amount_2021")
    util.remove_record(cr, "l10n_ke_hr_payroll.rule_parameter_shif_min_basic_amount_2024")
    util.remove_record(cr, "l10n_ke_hr_payroll.rule_parameter_shif_min_basic")
