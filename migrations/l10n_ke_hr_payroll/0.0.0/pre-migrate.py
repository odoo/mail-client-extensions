from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.util.hr_payroll import remove_salary_rule


def migrate(cr, version):
    if util.version_between("16.0", "17.0"):
        _fix_oversights(cr)


def _fix_oversights(cr):
    eb = util.expand_braces

    # l10n_ke_hr_payroll/data/hr_salary_rule_data.xml
    util.rename_xmlid(cr, *eb("l10n_ke_hr_payroll.l10n_ke_employees{_salary,}_insurance_relief"))

    remove_salary_rule(cr, "l10n_ke_hr_payroll.l10n_ke_employees_salary_mortgage_interest")
    remove_salary_rule(cr, "l10n_ke_hr_payroll.l10n_ke_employees_salary_nssf")

    # l10n_ke_hr_payroll/data/hr_salary_rule_category_data.xml
    util.rename_xmlid(cr, *eb("l10n_ke_hr_payroll.{hr_salary_rule_category_relief,RELIEF}"))
    util.rename_xmlid(cr, *eb("l10n_ke_hr_payroll.{hr_salary_rule_category_tax_exemption,EXEMPTION}"))

    # l10n_ke_hr_payroll/views/hr_employee_views.xml
    util.remove_view(cr, "l10n_ke_hr_payroll.hr_employee_view_form")
