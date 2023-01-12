# -*- coding: utf-8 -*-

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

    util.rename_module(cr, "l10n_hr", "l10n_hr_kuna")
    util.rename_module(cr, "l10n_hr_euro", "l10n_hr")

    util.force_upgrade_of_fresh_module(cr, "sale_service", init=False)
