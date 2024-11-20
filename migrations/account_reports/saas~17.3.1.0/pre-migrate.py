from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_reports.journal_report_pdf_export_filters")
    util.remove_view(cr, "account_reports.journal_report_pdf_export_main_table_header")
    util.remove_view(cr, "account_reports.journal_report_pdf_export_main_table_body")
    util.remove_record(cr, "account_reports.journal_report_date")
    util.remove_record(cr, "account_reports.journal_report_communication")
    util.remove_record(cr, "account_reports.journal_report_partner_name")
    util.remove_record(cr, "account_reports.journal_report_amount_currency")
    util.rename_field(cr, "account.report.file.download.error.wizard", "file_generation_errors", "actionable_errors")
    util.remove_record(cr, "account_reports.account_financial_report_executivesummary_net_assets0_na_balance")
    util.remove_record(cr, "account_reports.account_financial_report_executivesummary_avdebt0_deb")
    util.remove_record(cr, "account_reports.account_financial_report_executivesummary_avgcre0_cre")

    if not util.version_gte("saas~17.4"):  # In case of upgrade to 17.3
        util.delete_unused(cr, "account_reports.mail_activity_type_tax_report_to_be_sent")
