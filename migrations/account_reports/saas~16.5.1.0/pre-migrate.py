from odoo.upgrade import util


def migrate(cr, version):
    for model in ("account.report.column", "account.report.expression"):
        util.change_field_selection_values(cr, model, "figure_type", {"none": "string"})

    util.remove_view(cr, "account_reports.journal_report_pdf_export_cell")
    util.remove_view(cr, "account_reports.journal_report_pdf_export_line")
    util.remove_view(cr, "account_reports.general_ledger_pdf_export_main")
    util.remove_view(cr, "account_reports.template_horizontal_group_display")
    util.remove_view(cr, "account_reports.pdf_export_cell_growth_comparison")
    util.remove_view(cr, "account_reports.pdf_export_line")
    util.remove_view(cr, "account_reports.filter_extra_options_template")
