# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.new_module(cr, "sale_project", deps={"sale_management", "project"}, auto_install=True)
    util.new_module(
        cr, "sale_purchase_stock", deps={"sale_stock", "purchase_stock", "sale_purchase"}, auto_install=True
    )
    util.new_module(cr, "sale_stock_margin", deps={"stock_account", "sale_margin"}, auto_install=True)
    util.new_module(cr, "timer", deps={"web", "mail"})
    util.new_module(cr, "test_timer", deps={"timer"})

    util.module_deps_diff(cr, "hr_timesheet", plus={"timer"})
    util.merge_module(cr, "l10n_cn_small_business", "l10n_cn")
    util.module_deps_diff(cr, "l10n_id", plus={"l10n_multilang"})
    util.module_deps_diff(cr, "sale_timesheet", plus={"sale_project"}, minus={"sale_management"})
    util.module_deps_diff(
        cr, "stock_dropshipping", plus={"sale_purchase_stock"}, minus={"sale_stock", "purchase_stock", "sale_purchase"}
    )
    util.merge_module(cr, "pos_kitchen_printer", "pos_restaurant")
    util.merge_module(cr, "hr_holidays_calendar", "hr_holidays")

    if util.has_enterprise():
        util.new_module(cr, "account_inter_company_rules", deps={"account"})
        util.new_module(cr, "data_merge", deps={"web", "mail"})
        util.new_module(cr, "data_merge_crm", deps={"data_merge", "crm"}, auto_install=True)
        util.new_module(cr, "data_merge_utm", deps={"data_merge", "utm"}, auto_install=True)
        util.new_module(cr, "hr_expense_predict_product", deps={"hr_expense"}, auto_install=True)
        util.new_module(
            cr,
            "hr_expense_extract",
            deps={"hr_expense", "iap", "mail_enterprise", "hr_expense_predict_product"},
            auto_install=True,  # WTF?
        )
        util.new_module(cr, "industry_fsm_forecast", deps={"industry_fsm", "project_forecast"}, auto_install=True)
        util.new_module(
            cr, "quality_control_picking_batch", deps={"quality_control", "stock_picking_batch"}, auto_install=True
        )
        util.new_module(
            cr, "stock_barcode_picking_batch", deps={"stock_barcode", "stock_picking_batch"}, auto_install=True
        )
        util.new_module(
            cr,
            "stock_barcode_quality_control_picking_batch",
            deps={"quality_control_picking_batch", "stock_barcode_quality_control"},
            auto_install=True,
        )

        util.module_deps_diff(cr, "event_enterprise", plus={"web_gantt", "web_map"})
        util.module_deps_diff(cr, "helpdesk_timesheet", plus={"timer"})
        util.module_deps_diff(cr, "industry_fsm", plus={"base_geolocalize"})
        util.module_deps_diff(cr, "web_studio", plus={"web_map", "web_gantt", "sms"})

        util.rename_module(cr, "inter_company_rules", "sale_purchase_inter_company_rules")
        util.module_deps_diff(cr, "sale_purchase_inter_company_rules", plus={"account_inter_company_rules"})
        util.module_auto_install(cr, "sale_purchase_inter_company_rules", True)

        util.merge_module(cr, "hr_holidays_gantt_calendar", "hr_holidays_gantt")

    util.remove_module(cr, "partner_autocomplete_address_extended")
