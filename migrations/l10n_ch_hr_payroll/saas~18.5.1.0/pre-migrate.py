from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "l10n_ch_hr_payroll.action_report_payslip_ch")
    util.remove_record(cr, "l10n_ch_hr_payroll.action_report_light_payslip_ch")
    util.remove_record(cr, "l10n_ch_hr_payroll.action_report_monthly_summary")
    util.remove_record(cr, "l10n_ch_hr_payroll.action_report_individual_account")
    util.remove_record(cr, "l10n_ch_hr_payroll.action_insurance_yearly_report")
    util.remove_record(cr, "l10n_ch_hr_payroll.action_is_report")
