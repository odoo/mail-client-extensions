from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, "l10n_au_hr_payroll_account.hr_department_rdau", "l10n_au_hr_payroll.au_hr_department_rd")
    util.rename_xmlid(
        cr, "l10n_au_hr_payroll_account.job_developer_australian", "l10n_au_hr_payroll.au_hr_job_developer"
    )
    util.rename_xmlid(cr, *eb("l10n_au_hr_payroll.hr_employee_{au,roger}"))
    util.rename_xmlid(cr, *eb("l10n_au_hr_payroll.hr_contract_{au,roger}"))
    util.rename_xmlid(cr, *eb("l10n_au_hr_payroll{_account,}.res_partner_dennis"))
    util.rename_xmlid(cr, *eb("l10n_au_hr_payroll{_account,}.user_dennis"))
    util.rename_xmlid(cr, *eb("l10n_au_hr_payroll{_account,}.res_partner_dennis_work_address"))
    util.rename_xmlid(cr, *eb("l10n_au_hr_payroll{_account,}.res_partner_dennis_private_address"))
    util.rename_xmlid(cr, *eb("l10n_au_hr_payroll{_account,}.res_partner_bank_account_dennis"))
    util.rename_xmlid(cr, *eb("l10n_au_hr_payroll{_account,}.hr_employee_dennis"))
    util.rename_xmlid(cr, *eb("l10n_au_hr_payroll{_account,}.hr_contract_cdi_dennis_previous"))
    util.rename_xmlid(cr, *eb("l10n_au_hr_payroll{_account,}.hr_contract_cdi_dennis"))

    util.remove_record(cr, "l10n_au_hr_payroll.l10n_au_payslip_employee_bank_account")
    util.remove_record(cr, "l10n_au_hr_payroll.res_partner_employee_au")
