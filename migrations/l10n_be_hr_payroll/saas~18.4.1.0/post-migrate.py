from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "l10n_be_hr_payroll.hr_payroll_dashboard_warning_invalid_work_address")
    util.update_record_from_xml(cr, "l10n_be_hr_payroll.hr_payroll_dashboard_warning_invalid_sex")
