from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "l10n_be_reports.account_financial_report_be_actif0")
    util.remove_record(cr, "l10n_be_reports.account_financial_report_be_passif0")
    util.remove_record(cr, "l10n_be_reports.account_financial_report_be_empty")
    util.remove_record(cr, "l10n_be_reports.account_financial_report_be_empty2")
    util.remove_record(cr, "l10n_be_reports.account_financial_report_be_empty3")
    util.remove_record(cr, "l10n_be_reports.account_financial_report_be_empty4")
    util.remove_record(cr, "l10n_be_reports.account_financial_report_be_empty5")
    util.remove_record(cr, "l10n_be_reports.account_financial_report_be_empty6")
