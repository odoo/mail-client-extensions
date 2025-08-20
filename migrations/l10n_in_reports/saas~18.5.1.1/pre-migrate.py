from odoo.upgrade import util


def migrate(cr, version):
    report_line_records = [
        util.ref(cr, "l10n_in_reports.account_report_gstr1_b2b"),
        util.ref(cr, "l10n_in_reports.account_report_gstr1_nil"),
    ]

    report_expression_records = [
        util.ref(cr, "l10n_in_reports.account_report_gstr1_b2b_taxable_amount_balance"),
        util.ref(cr, "l10n_in_reports.account_report_gstr1_b2b_sgst_balance"),
        util.ref(cr, "l10n_in_reports.account_report_gstr1_b2b_cgst_balance"),
        util.ref(cr, "l10n_in_reports.account_report_gstr1_b2b_igst_balance"),
        util.ref(cr, "l10n_in_reports.account_report_gstr1_b2b_cess_balance"),
        util.ref(cr, "l10n_in_reports.account_report_gstr1_nil_taxable_amount_balance"),
    ]

    util.remove_records(cr, "account.report.line", report_line_records)
    util.remove_records(cr, "account.report.expression", report_expression_records)

    util.remove_view(cr, "l10n_in_reports.l10n_in_gst_return_period_form_view_document_summary")
