from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "l10n_us_hr_payroll_state_calculation", "l10n_us_hr_payroll")
    util.merge_module(cr, "l10n_in_reports_gstr_spreadsheet", "l10n_in_reports_gstr")
    util.merge_module(cr, "l10n_in_withholding_payment", "l10n_in_withholding")
