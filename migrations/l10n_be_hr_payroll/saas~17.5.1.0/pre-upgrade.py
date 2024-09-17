from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_be_hr_payroll.report_double_holiday_13th_month")
    util.remove_record(cr, "l10n_be_hr_payroll.action_report_double_holiday_13th_month")
