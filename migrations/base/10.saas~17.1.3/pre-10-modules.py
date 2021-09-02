# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # NOTE: `report` module handled in `pre-20` script
    eb = util.expand_braces
    util.new_module(cr, "account_invoicing", deps=("account",), auto_install=True)
    util.new_module(cr, "base_vat_autocomplete", deps=("base_vat",), auto_install=True)

    util.module_deps_diff(cr, "account_accountant", plus={"account_invoicing"}, minus={"account"})

    util.new_module_dep(cr, "crm", "contacts")

    util.module_deps_diff(cr, "hr_timesheet_attendance", plus={"hr_timesheet"}, minus={"hr_timesheet_sheet"})

    for cc in "at ca co ec et mx si syscohada tr ve vn".split():
        util.module_deps_diff(cr, "l10n_" + cc, plus={"account"}, minus={"base_vat"})
    util.new_module_dep(cr, "l10n_it", "account")
    util.new_module_dep(cr, "l10n_uk", "account")

    util.module_deps_diff(cr, "sale", minus={"web_tour"})
    util.new_module(cr, "sale_management", deps={"sale", "account_invoicing"}, auto_install=True)
    sale_modules = """
        event_sale mrp_repair pos_sale report_intrastat sale_expense sale_margin sale_stock
        sale_timesheet website_quote
    """
    for module in sale_modules.split():
        util.module_deps_diff(cr, module, plus={"sale_management"}, minus={"sale"})

    util.new_module(cr, "sale_payment", deps={"sale", "payment"})

    util.rename_module(cr, "stock_picking_wave", "stock_picking_batch")

    util.new_module(
        cr,
        "website_account",
        deps={"account", "website_portal", "website_payment"},
        auto_install=util.module_installed(cr, "website_portal_sale"),
    )
    util.rename_xmlid(cr, *eb("website_{portal_sale,account}.portal_my_home_menu_invoice"), False)
    util.rename_xmlid(cr, *eb("website_{portal_sale,account}.portal_my_home_invoice"), False)
    util.rename_xmlid(cr, *eb("website_{portal_sale,account}.portal_my_invoices"), False)

    util.new_module_dep(cr, "website_portal_sale", "sale_payment")
    util.new_module(cr, "website_rating", deps={"rating", "website_mail"}, auto_install=True)
    util.module_deps_diff(
        cr,
        "website_sale",
        plus={"website_account", "website_rating", "sale_payment"},
        minus={"rating", "sale", "payment"},
    )
    util.module_deps_diff(cr, "website_sale_digital", plus={"website_portal_sale"}, minus={"website_sale"})

    util.new_module(cr, "website_sale_management", deps={"sale_management", "website_sale"}, auto_install=True)

    if util.has_enterprise():
        util.rename_module(cr, "sale_contract", "sale_subscription")
        util.rename_module(cr, "sale_contract_asset", "sale_subscription_asset")
        util.rename_module(cr, "account_contract_dashboard", "sale_subscription_dashboard")
        util.rename_module(cr, "website_contract", "website_subscription")

        util.new_module(cr, "account_3way_match", deps={"purchase"})
        util.new_module(cr, "delivery_bpost", deps={"delivery", "mail"})
        util.new_module(cr, "l10n_us_reports", deps={"l10n_us", "account_reports"}, auto_install=True)
        util.new_module(cr, "website_delivery_ups", deps={"delivery_ups", "website_sale_delivery"}, auto_install=True)
        util.new_module(
            cr, "website_quote_subscription", deps={"sale_subscription", "website_quote"}, auto_install=True
        )

        sale_modules = """
            inter_company_rules print_sale project_forecast_sale sale_coupon sale_ebay
            sale_subscription
        """
        for module in sale_modules.split():
            util.module_deps_diff(cr, module, plus={"sale_management"}, minus={"sale"})

        util.module_deps_diff(cr, "project_timesheet_synchro", plus={"hr_timesheet"}, minus={"hr_timesheet_sheet"})
        util.module_deps_diff(cr, "sale_subscription_asset", plus={"account_deferred_revenue"}, minus={"account_asset"})
        util.new_module_dep(cr, "website_form_editor", "website_enterprise")
        util.module_deps_diff(
            cr, "website_subscription", minus={"website_sale", "website_quote", "sale_subscription_dashboard"}
        )

    util.force_migration_of_fresh_module(cr, "sale_payment")
    util.force_migration_of_fresh_module(cr, "website_account")

    # farewell ...
    util.remove_module(cr, "hr_timesheet_sheet")  # XXX merged into hr_timesheet?
    if util.has_enterprise():
        util.remove_module(cr, "hr_timesheet_sheet_timesheet_grid")
