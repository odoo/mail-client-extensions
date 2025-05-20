from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("l10n_lt_hr_payroll.{hr_department_rdlt,lt_hr_department_rd}"))
    util.rename_xmlid(cr, *eb("l10n_lt_hr_payroll.{job_developer_lithuania,lt_hr_job_developer}"))
    util.rename_xmlid(cr, *eb("l10n_lt_hr_payroll.hr_contract_{cdi_,}norberta_previous"))
    util.rename_xmlid(cr, *eb("l10n_lt_hr_payroll.hr_contract_{cdi_,}norberta"))

    util.remove_record(cr, "l10n_lt_hr_payroll.res_partner_norberta_private_address")

    columns = [
        "l10n_lt_working_capacity",
    ]
    move_columns = util.import_script("l10n_au_hr_payroll/saas~18.4.1.0/pre-migrate.py").move_columns
    move_columns(cr, employee_columns=columns)
