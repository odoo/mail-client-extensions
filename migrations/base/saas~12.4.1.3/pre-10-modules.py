# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.new_module(
        cr, "account_analytic_default_purchase", deps={"account_analytic_default", "purchase"}, auto_install=True
    )
    util.new_module(cr, "hr_skills_slides", deps={"hr_skills", "website_slides"}, auto_install=True)
    util.new_module(cr, "hr_skills_survey", deps={"hr_skills", "survey"}, auto_install=True)
    util.new_module(cr, "payment_alipay", deps={"payment"})
    util.new_module(cr, "sale_timesheet_purchase", deps={"sale_timesheet", "purchase"}, auto_install=True)

    util.module_deps_diff(cr, "account_analytic_default", plus={"account"}, minus={"sale_stock"})
    util.module_deps_diff(cr, "crm", plus={"phone_validation"})
    util.module_deps_diff(cr, "mass_mailing_sale", minus={"website_sale_link_tracker"})
    util.module_deps_diff(cr, "membership", minus={"base", "product"})
    util.module_deps_diff(cr, "portal", plus={"auth_signup"})  # see https://github.com/odoo/odoo/pull/36477
    util.module_deps_diff(cr, "project", plus={"analytic"})
    util.module_deps_diff(cr, "sale", plus={"utm"})
    util.module_deps_diff(cr, "website_crm", minus={"website_partner"})
    util.module_deps_diff(cr, "website_crm_phone_validation", minus={"crm_phone_validation"})
    util.module_deps_diff(cr, "website_slides_survey", plus={"survey"}, minus={"website_survey"})

    util.ENVIRON["account_voucher_installed"] = util.module_installed(cr, "account_voucher")
    util.merge_module(cr, "account_voucher", "account")
    util.merge_module(cr, "crm_phone_validation", "crm")
    util.merge_module(cr, "mrp_bom_cost", "mrp_account")

    if util.has_enterprise():
        util.new_module(cr, "web_map", deps={"web"}, auto_install=True)
        util.new_module(cr, "hr_contract_reports", deps={"hr_contract", "web_dashboard"}, auto_install=True)
        util.new_module(cr, "industry_fsm_stock", deps={"industry_fsm", "sale_stock"}, auto_install=True)
        util.new_module(cr, "map_view_contact", deps={"contacts", "web_map"}, auto_install=True)
        util.new_module(cr, "purchase_enterprise", deps={"purchase", "web_dashboard"}, auto_install={"purchase"})

        # The `sale_rental` module create a name conflict with one module of OCA [1] and has been renamed in saas~12.5
        # We therefore forbid upgrades to saas~12.4 (as final version). The modules will be created in the saas~12.5 script
        # [1] https://twitter.com/PedroMBaeza/status/1151530523807891456
        assert util.version_gte("saas~12.5")

        util.module_deps_diff(cr, "account_accountant", plus={"mail_enterprise"})
        util.module_deps_diff(cr, "helpdesk_timesheet", plus={"project_enterprise"})
        util.module_deps_diff(cr, "hr_appraisal", minus={"survey"})
        util.module_deps_diff(cr, "hr_payroll", plus={"web_dashboard"})
        util.module_deps_diff(cr, "l10n_be_hr_payroll", plus={"hr_contract_reports"})
        util.module_deps_diff(cr, "mrp_mps", plus={"purchase_stock"}, minus={"purchase"})
        util.module_deps_diff(cr, "project_enterprise", plus={"web_map"})
        util.module_deps_diff(cr, "project_forecast", plus={"web_gantt"})
        util.module_deps_diff(cr, "stock_enterprise", plus={"web_map"})
        util.module_deps_diff(cr, "stock_account_enterprise", plus={"stock_enterprise"})
        util.module_deps_diff(cr, "web_mobile", plus={"base_setup"}, minus={"web_settings_dashboard"})

        util.merge_module(cr, "hr_payroll_gantt", "hr_payroll")
        util.merge_module(cr, "website_form_editor", "website_form")

        util.remove_module(cr, "l10n_mx_edi_sale_coupon")

        util.module_auto_install(cr, "crm_enterprise", {"crm"})
        util.module_auto_install(cr, "im_livechat_enterprise", {"im_livechat"})
        util.module_auto_install(cr, "ocn_client", False)
        util.module_auto_install(cr, "sale_enterprise", {"sale"})
        util.module_auto_install(cr, "stock_account_enterprise", {"stock_account"})
        util.module_auto_install(cr, "stock_enterprise", {"stock"})
        util.module_auto_install(cr, "web_dashboard", False)
        util.module_auto_install(cr, "website_sale_dashboard", {"website_sale"})

    util.remove_module(cr, "event_sale_product_configurator")

    for field in {"campaign_id", "medium_id", "source_id"}:
        util.move_field_to_module(cr, "sale.order", field, "website_sale_link_tracker", "sale")
        util.move_field_to_module(cr, "sale.report", field, "website_sale_link_tracker", "sale")

    util.remove_module(cr, "website_sale_link_tracker")
    util.remove_module(cr, "website_survey")  # merged?
