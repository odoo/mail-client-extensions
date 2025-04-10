from odoo.upgrade import util


def migrate(cr, version):
    util.ENVIRON["predictive_bills_installed"] = util.module_installed(cr, "account_predictive_bills")
    util.remove_module(cr, "pos_cache")
    util.remove_module(cr, "spreadsheet_dashboard_sale_expense")
    util.remove_module(cr, "association")

    if util.has_enterprise():
        util.remove_module(cr, "account_predictive_bills")
        util.remove_module(cr, "project_timesheet_forecast_contract")
        util.remove_module(cr, "event_sale_dashboard")
        util.merge_module(cr, "sale_enterprise", "sale")
        util.merge_module(cr, "l10n_de_datev_reports", "l10n_de_reports")
        # l10n_pe_reports was renamed in saas~16.1, both l10n_pe_reports_book and l10n_pe_reports
        # coexisted until saas~16.4 where they were merged
        util.rename_module(cr, "l10n_pe_reports", "l10n_pe_reports_book")

    util.rename_module(cr, "l10n_hr", "l10n_hr_kuna")
    util.rename_module(cr, "l10n_hr_euro", "l10n_hr")

    util.force_upgrade_of_fresh_module(cr, "sale_service", init=False)

    if util.module_installed(cr, "account_invoice_extract"):
        util.force_upgrade_of_fresh_module(cr, "iap_extract")

    # sale is a new dependency of spreadsheet_dashboard_hr_expense
    if util.module_installed(cr, "spreadsheet_dashboard_hr_expense"):
        util.create_column(cr, "account_move", "team_id", "int4")
