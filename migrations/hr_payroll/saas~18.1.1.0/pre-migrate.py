from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_salary_rule_category", "country_id", "int4")

    if util.module_installed(cr, "l10n_ma_hr_payroll"):
        util.remove_record(cr, "l10n_ma_hr_payroll.COMP")
