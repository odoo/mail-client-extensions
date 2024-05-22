from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "l10n_cl_reports.account_financial_report_f29_line_0103")
    util.remove_record(cr, "l10n_cl_reports.account_financial_report_f29_line_0103_balance")

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("l10n_cl_reports.account_financial_report_f29_line_010{4,3}"))
    util.rename_xmlid(cr, *eb("l10n_cl_reports.account_financial_report_f29_line_010{4,3}_balance"))
    util.rename_xmlid(cr, *eb("l10n_cl_reports.account_financial_report_f29_line_010{5,4}"))
    util.rename_xmlid(cr, *eb("l10n_cl_reports.account_financial_report_f29_line_010{5,4}_balance"))
