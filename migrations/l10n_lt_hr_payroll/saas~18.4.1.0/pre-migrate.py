from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("l10n_lt_hr_payroll.{hr_department_rdlt,lt_hr_department_rd}"))
    util.rename_xmlid(cr, *eb("l10n_lt_hr_payroll.{job_developer_lithuania,lt_hr_job_developer}"))
    util.rename_xmlid(cr, *eb("l10n_lt_hr_payroll.hr_contract_{cdi_,}norberta_previous"))
    util.rename_xmlid(cr, *eb("l10n_lt_hr_payroll.hr_contract_{cdi_,}norberta"))

    util.remove_record(cr, "l10n_lt_hr_payroll.res_partner_norberta_private_address")
