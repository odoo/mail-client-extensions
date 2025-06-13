from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("l10n_nl_hr_payroll.{hr_department_rdnl,nl_hr_department_rd}"))
    util.rename_xmlid(cr, *eb("l10n_nl_hr_payroll.{job_developer_dutch,nl_hr_job_developer}"))
    util.rename_xmlid(cr, *eb("l10n_nl_hr_payroll.hr_contract_{cdi_,}lotte_previous"))
    util.rename_xmlid(cr, *eb("l10n_nl_hr_payroll.hr_contract_{cdi_,}lotte"))
    util.rename_xmlid(cr, *eb("l10n_nl_hr_payroll.hr_contract_{,template_}view_form"))

    util.remove_record(cr, "l10n_nl_hr_payroll.res_partner_lotte_work_address")
    util.remove_record(cr, "l10n_nl_hr_payroll.res_partner_lotte_private_address")
