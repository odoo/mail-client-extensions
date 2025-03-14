from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_report_footnote", "report_id", "integer")
    cr.execute(
        """
        UPDATE account_report_footnote footnote
           SET report_id = manager.report_id
          FROM account_report_manager manager
         WHERE manager.id = footnote.manager_id
        """
    )

    util.remove_asset(cr, "account_reports.assets_financial_report")
    util.remove_model(cr, "account.report.manager")

    util.remove_view(cr, "account_reports.filter_info_template_journal_audit_report")
    util.remove_view(cr, "account_reports.main_template_journal_audit_report")
    util.remove_view(cr, "account_reports.search_template_journal_audit_report")
    util.remove_view(cr, "account_reports.search_template_extra_options_journal_audit_report")
    util.remove_view(cr, "account_reports.line_template_journal_audit_report")
    util.remove_view(cr, "account_reports.cell_template_journal_audit_report")
    util.remove_view(cr, "account_reports.main_table_header_journal_audit_report")
    util.remove_view(cr, "account_reports.multicurrency_report_line_template")
    util.remove_view(cr, "account_reports.multicurrency_report_main_template")
    util.remove_view(cr, "account_reports.multicurrency_report_search_template")
    util.remove_view(cr, "account_reports.template_partner_ledger_report")
    util.remove_view(cr, "account_reports.line_template_partner_ledger_report")
    util.remove_view(cr, "account_reports.ec_sales_with_tax_filter_search_template")
    util.remove_view(cr, "account_reports.sales_report_main_template")
    util.remove_view(cr, "account_reports.bank_reconciliation_report_cell_template_unexplained_difference")
    util.remove_view(cr, "account_reports.bank_reconciliation_report_cell_template_link_last_statement")
    util.remove_view(cr, "account_reports.bank_reconciliation_report_main_template")
    util.remove_view(cr, "account_reports.line_template_general_ledger_report")
    util.remove_view(cr, "account_reports.template_general_ledger_report")
    util.remove_view(cr, "account_reports.aged_report_main_template")
    util.remove_view(cr, "account_reports.aged_report_line_template")
    util.remove_view(cr, "account_reports.search_template_tax_unit")
    util.remove_view(cr, "account_reports.template_tax_report")
    util.remove_view(cr, "account_reports.search_template")
    util.remove_view(cr, "account_reports.search_template_fiscal_position_choser")
    util.remove_view(cr, "account_reports.search_template_variants")
    util.remove_view(cr, "account_reports.search_template_partner")
    util.remove_view(cr, "account_reports.search_template_groupby_fields")
    util.remove_view(cr, "account_reports.search_template_horizontal_groups")
    util.remove_view(cr, "account_reports.search_template_analytic")
    util.remove_view(cr, "account_reports.search_template_account_type")
    util.remove_view(cr, "account_reports.search_template_journals")
    util.remove_view(cr, "account_reports.search_template_extra_options")
    util.remove_view(cr, "account_reports.search_template_comparison")
    util.remove_view(cr, "account_reports.search_template_date_filter")
    util.remove_view(cr, "account_reports.print_template")
    util.remove_view(cr, "account_reports.main_template_with_filter_input_accounts")
    util.remove_view(cr, "account_reports.cell_template_debug_column")
    util.remove_view(cr, "account_reports.cell_template_growth_comparison")
    util.remove_view(cr, "account_reports.main_template_trial_balance")
    util.remove_view(cr, "account_reports.main_template")
    util.remove_view(cr, "account_reports.main_table_header")
    util.remove_view(cr, "account_reports.line_template")
    util.remove_view(cr, "account_reports.cell_template")
    util.remove_view(cr, "account_reports.filter_info_template")
    util.remove_view(cr, "account_reports.line_caret_options")
    util.remove_view(cr, "account_reports.footnotes_template")

    util.remove_field(cr, "account.report", "search_template")
    util.remove_field(cr, "account.report", "footnotes_template")
    util.remove_field(cr, "account.report", "line_template")
    util.remove_field(cr, "account.report", "main_table_header_template")
    util.remove_field(cr, "account.report", "main_template")
    util.remove_field(cr, "account.report.footnote", "manager_id")
    util.rename_field(cr, "account.report.footnote", "line", "line_id")
