from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        "SELECT 1 FROM account_report_line WHERE id = %s AND code='CL_VEXPO'",
        [util.ref(cr, "l10n_cl_reports.account_financial_report_f29_line_0103")],
    )
    if not cr.rowcount:
        return

    util.remove_record(cr, "l10n_cl_reports.account_financial_report_f29_line_0103")
    util.remove_record(cr, "l10n_cl_reports.account_financial_report_f29_line_0103_balance")

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("l10n_cl_reports.account_financial_report_f29_line_010{4,3}"))
    util.rename_xmlid(cr, *eb("l10n_cl_reports.account_financial_report_f29_line_010{4,3}_balance"))
    util.rename_xmlid(cr, *eb("l10n_cl_reports.account_financial_report_f29_line_010{5,4}"))
    util.rename_xmlid(cr, *eb("l10n_cl_reports.account_financial_report_f29_line_010{5,4}_balance"))
