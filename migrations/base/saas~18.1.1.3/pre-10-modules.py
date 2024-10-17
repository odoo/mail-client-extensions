from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "l10n_us_hr_payroll_state_calculation", "l10n_us_hr_payroll")
    util.merge_module(cr, "l10n_in_reports_gstr_spreadsheet", "l10n_in_reports_gstr")
    util.merge_module(cr, "l10n_in_withholding_payment", "l10n_in_withholding")
    util.merge_module(cr, "auth_totp_mail_enforce", "auth_totp_mail")
    util.rename_module(cr, "l10n_in_edi_ewaybill", "l10n_in_ewaybill")
    if util.has_enterprise():
        util.merge_module(cr, "l10n_nl_reports_sbr", "l10n_nl_reports")
        util.merge_module(cr, "l10n_nl_reports_sbr_ob_nummer", "l10n_nl_reports")
        util.merge_module(cr, "l10n_nl_reports_sbr_status_info", "l10n_nl_reports")
        util.merge_module(cr, "l10n_nl_reports_sbr_icp", "l10n_nl_reports")
