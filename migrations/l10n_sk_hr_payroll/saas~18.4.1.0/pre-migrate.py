from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("l10n_sk_hr_payroll.{hr_department_rdpl,sk_hr_department_rd}"))
    util.rename_xmlid(cr, *eb("l10n_sk_hr_payroll.{job_developer_slovakia,sk_hr_job_developer}"))
    util.rename_xmlid(cr, *eb("l10n_sk_hr_payroll.hr_contract_{cdi_,}frantiska_previous"))
    util.rename_xmlid(cr, *eb("l10n_sk_hr_payroll.hr_contract_{cdi_,}frantiska"))
    util.rename_xmlid(cr, *eb("l10n_sk_hr_payroll.hr_contract_{,template_}view_form"))

    util.remove_record(cr, "l10n_sk_hr_payroll.res_partner_bank_account_norberta")
    util.remove_record(cr, "l10n_sk_hr_payroll.res_partner_frantiska_work_address")
    util.remove_record(cr, "l10n_sk_hr_payroll.res_partner_frantiska_private_address")
