from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{hr_department_rdlt,mx_hr_department_rd}"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{job_developer_lithuania,mx_hr_job_developer}"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.res_partner_{cesar,mx}_work_address"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.res_partner_{cesar,mx}_private_address"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.hr_contract_{cdi_,}cecilia_previous"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.hr_contract_{cdi_,}cecilia"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.hr_contract_{cdi_,}cesar"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.hr_contract_{cdi_,}karla"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.hr_contract_{cdi_xochilt,xochitl}"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.hr_contract_{,template_}view_form"))

    util.remove_record(cr, "l10n_mx_hr_payroll.res_partner_cecilia_work_address")
    util.remove_record(cr, "l10n_mx_hr_payroll.res_partner_cecilia_private_address")

    util.rename_field(cr, "l10n.mx.hr.fonacot", "contract_id", "version_id")
    util.rename_field(cr, "l10n.mx.hr.infonavit", "contract_id", "version_id")
