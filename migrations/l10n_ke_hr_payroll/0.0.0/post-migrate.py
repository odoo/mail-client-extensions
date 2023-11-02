from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("16.0", "17.0"):
        util.delete_unused(cr, "l10n_ke_hr_payroll.hr_salary_rule_category_paye")
