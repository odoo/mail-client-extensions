from odoo.upgrade import util


def migrate(cr, version):
    util.delete_unused(cr, "l10n_lu_hr_payroll.l10n_lu_employees_atn_transport")
    util.delete_unused(cr, "l10n_lu_hr_payroll.hr_salary_rule_category_bik_transport")
