from odoo.upgrade import util
from odoo.upgrade.util.hr_payroll import remove_salary_rule


def migrate(cr, version):
    xmlid = "l10n_in_hr_payroll.l10n_in_contract_type_intern"
    intern = util.ref(cr, "hr.contract_type_intern")
    if intern is not None:
        util.replace_record_references_batch(cr, {util.ref(cr, xmlid): intern}, "hr.contract.type", replace_xmlid=False)
        util.remove_record(cr, xmlid)
    else:
        util.delete_unused(cr, xmlid)

    util.make_field_non_stored(cr, "hr.version", "l10n_in_provident_fund", selectable=True)
    util.remove_field(cr, "hr.version", "l10n_in_voluntary_provident_fund")
    util.remove_field(cr, "hr.version", "l10n_in_driver_salay")
    util.rename_field(cr, "hr.version", "l10n_in_house_rent_allowance_metro_nonmetro", "l10n_in_hra_percentage")
    util.rename_field(cr, "hr.version", "l10n_in_supplementary_allowance", "l10n_in_fixed_allowance")
    util.rename_field(cr, "hr.version", "l10n_in_esic_amount", "l10n_in_esic_employee_amount")
    remove_salary_rule(cr, "l10n_in_hr_payroll.l10n_in_hr_salary_rule_bonus")
    remove_salary_rule(cr, "l10n_in_hr_payroll.hr_payslip_rule_vpf")
    remove_salary_rule(cr, "l10n_in_hr_payroll.hr_salary_rule_driver")
    remove_salary_rule(cr, "l10n_in_hr_payroll.l10n_in_hr_salary_rule_leave")
    util.remove_field(cr, "hr.version", "l10n_in_leave_allowance")
