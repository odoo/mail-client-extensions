from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_model(cr, "l10n.be.report.partner.vat.listing")
    util.remove_view(cr, "l10n_be_reports.line_caret_options")
    for i in [0, 3, 4, 5, 8, 9, 10, 13, 14, 16, 17, 18, 29]:
        util.remove_record(cr, f"l10n_be_reports.account_financial_report_be_{i}_control")
        util.remove_record(cr, f"l10n_be_reports.account_financial_report_be_{i}_control_balance")
        util.remove_record(cr, f"l10n_be_reports.account_financial_report_be_{i}_control_be_{i}_total_balance")
    util.remove_record(cr, "l10n_be_reports.account_financial_report_be_off_sheet")
