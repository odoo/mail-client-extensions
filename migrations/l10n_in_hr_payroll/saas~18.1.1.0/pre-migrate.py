from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "l10n_in_hr_payroll.light_payslip_details_report")
    util.remove_view(cr, "l10n_in_hr_payroll.report_light_payslip_details")
    util.remove_view(cr, "l10n_in_hr_payroll.report_light_payslip")
    util.remove_view(cr, "l10n_in_hr_payroll.report_payslip_details")
    util.remove_view(cr, "l10n_in_hr_payroll.l10n_in_to_pay")
