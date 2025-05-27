from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("l10n_pl_hr_payroll.{hr_department_rdpl,pl_hr_department_rd}"))
    util.rename_xmlid(cr, *eb("l10n_pl_hr_payroll.{job_developer_poland,pl_hr_job_developer}"))
    util.rename_xmlid(cr, *eb("l10n_pl_hr_payroll.hr_contract_{cdi_,}antonina_previous"))
    util.rename_xmlid(cr, *eb("l10n_pl_hr_payroll.hr_contract_{cdi_,}antonina"))

    util.remove_record(cr, "l10n_pl_hr_payroll.res_partner_bank_account_norberta")
    util.remove_record(cr, "l10n_pl_hr_payroll.res_partner_antonina_work_address")
    util.remove_record(cr, "l10n_pl_hr_payroll.res_partner_antonina_private_address")
