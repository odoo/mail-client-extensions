from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("l10n_us_hr_payroll.{hr_department_rdus,us_hr_department_rd}"))
    util.rename_xmlid(cr, *eb("l10n_us_hr_payroll.{job_developer_united_states,us_hr_job_developer}"))
    util.rename_xmlid(cr, *eb("l10n_us_hr_payroll.hr_contract_{cdi_,}maggie_previous"))
    util.rename_xmlid(cr, *eb("l10n_us_hr_payroll.hr_contract_{cdi_,}maggie"))

    util.remove_record(cr, "l10n_us_hr_payroll.res_partner_maggie_work_contact")
    util.remove_record(cr, "l10n_us_hr_payroll.res_partner_bank_account_norberta")
