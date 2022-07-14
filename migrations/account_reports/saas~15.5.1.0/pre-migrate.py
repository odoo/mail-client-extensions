# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("DELETE FROM account_report_manager")

    util.remove_field(cr, "account.report.manager", "financial_report_id")

    for model in (
        "account.financial.html.report.line",
        "account.financial.html.report",
        "account.aged.partner",
        "account.aged.receivable",
        "account.aged.payable",
        "account.analytic.report",
        "account.bank.reconciliation.report",
        "account.cash.flow.report",
        "account.general.ledger",
        "account.generic.tax.report",
        "account.multicurrency.revaluation",
        "account.journal.audit",
        "account.partner.ledger",
        "account.coa.report",
        "account.sales.report",
        "account.accounting.report",
        "account.generic.tax.report",
    ):
        util.remove_model(cr, model)

    for template in (
        "ec_sales_line_caret_options",
        "account_reports_sales_report_main_template",
        "bank_reconciliation_report_search_template",
        "bank_reconciliation_report_search_template_date_filter",
        "search_template_tax_unit_chooser",
        "search_template_tax_report_choser",
        "search_template_generic_tax_report",
        "search_template_ec_sale_code",
        "search_template_currency",
        "search_template_ir_filters",
        "line_template_multicurrency_report",
        "template_multicurrency_report",
        "line_template_aged_payable_report",
        "line_template_aged_receivable_report",
        "template_aged_partner_balance_report",
        "template_aged_partner_balance_line_report",
        "main_template_control_domain",
        "cell_template_popup_carryover",
        "cell_template_debug_popup_financial_reports",
        "cell_template_show_bug_financial_reports",
        "account_report_print_journal_view",
    ):
        util.remove_view(cr, f"account_reports.{template}")
