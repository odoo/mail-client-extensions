from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "l10n_lt_reports.account_financial_html_report_line_bs_lt_d_5_1_balance_account_codes")
    util.remove_record(cr, "l10n_lt_reports.account_financial_html_report_line_bs_lt_d_5_1_balance_aggregate")
    util.remove_record(cr, "l10n_lt_reports.account_financial_html_report_line_bs_lt_d_5_1_bs_pl_balance")
    util.remove_record(cr, "l10n_lt_reports.account_financial_html_report_line_bs_lt_d_5_2_balance_aggregate")
