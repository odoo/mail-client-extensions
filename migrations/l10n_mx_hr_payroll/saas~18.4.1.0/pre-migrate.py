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

    util.rename_xmlid(cr, *eb("{base,l10n_mx_hr_payroll}.hr_employee_cecilia"))
    util.rename_xmlid(cr, *eb("{base,l10n_mx_hr_payroll}.hr_employee_cesar"))
    util.rename_xmlid(cr, *eb("{base,l10n_mx_hr_payroll}.hr_employee_karla"))
    util.rename_xmlid(cr, "base.hr_employee_xochilt", "l10n_mx_hr_payroll.hr_employee_xochitl")

    util.remove_record(cr, "l10n_mx_hr_payroll.res_partner_cecilia_work_address")
    util.remove_record(cr, "l10n_mx_hr_payroll.res_partner_cecilia_private_address")
