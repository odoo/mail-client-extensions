# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_module(cr, "website_mail_channel")
    util.remove_module(cr, "website_sale_management")
    util.remove_module(cr, "website_sale_blog")
    cr.execute("DROP TABLE IF EXISTS product_blogpost_rel")

    if util.has_enterprise():
        util.remove_module(cr, "mail_github")
        util.new_module(cr, "hr_appraisal_skills", deps={"hr_appraisal", "hr_skills"}, auto_install=True)
        util.new_module(cr, "event_social", deps={"event", "social"}, auto_install=True)
        util.new_module(cr, "social_instagram", deps={"social"}, auto_install=False)
        util.module_deps_diff(cr, "social_demo", plus={"social_instagram"})
        util.module_deps_diff(cr, "social_test_full", plus={"social_instagram"})
        util.new_module(cr, "mrp_workorder_plm", deps={"mrp_workorder", "mrp_plm"}, auto_install=True)
        util.new_module(cr, "project_account_budget", deps={"account_budget", "project"}, auto_install=True)

        util.module_deps_diff(cr, "l10n_co_edi", plus={"account_edi"}, minus={"account"})

        util.rename_module(cr, "crm_enterprise_iap_lead_website", "website_crm_iap_reveal_enterprise")
        util.rename_module(cr, "website_calendar", "appointment")
        util.module_deps_diff(cr, "appointment", plus={"portal"}, minus={"website_enterprise"})
        util.rename_module(cr, "website_calendar_crm", "appointment_crm")
        util.new_module(cr, "website_appointment", deps={"appointment", "website_enterprise"}, auto_install=True)

        util.new_module(cr, "l10n_ae_reports", deps={"l10n_ae", "account_reports"}, auto_install=True)
        util.new_module(cr, "l10n_ae_hr_payroll", deps={"hr_payroll"})
        util.new_module(
            cr,
            "l10n_ae_hr_payroll_account",
            deps={"hr_payroll_account", "l10n_ae", "l10n_ae_hr_payroll"},
            auto_install=True,
        )
        util.remove_module(cr, "stock_barcode_mobile")
        util.module_deps_diff(cr, "stock_barcode", plus={"barcodes_gs1_nomenclature", "web_mobile"}, minus={"barcodes"})
        util.new_module(cr, "pos_settle_due", deps={"point_of_sale", "account_followup"}, auto_install=True)

        util.new_module(cr, "planning_hr_skills", deps={"planning", "hr_skills"}, auto_install=True)

        util.new_module(cr, "sale_planning", deps={"planning", "sale_management"}, auto_install=True)
        util.new_module(
            cr, "sale_project_forecast", deps={"project_forecast", "sale_project", "sale_planning"}, auto_install=True
        )
        util.new_module(cr, "planning_contract", deps={"planning", "hr_contract"}, auto_install=True)
        util.module_deps_diff(cr, "project_timesheet_forecast_sale", plus={"sale_project_forecast"})
        util.force_migration_of_fresh_module(cr, "sale_planning")
        util.force_migration_of_fresh_module(cr, "sale_project_forecast")
        util.merge_module(cr, "l10n_lu_reports_electronic", "l10n_lu_reports")
        util.merge_module(cr, "l10n_lu_reports_electronic_xml_2_0", "l10n_lu_reports")
        util.merge_module(cr, "l10n_lu_saft", "l10n_lu_reports")
        util.module_deps_diff(cr, "l10n_lu_reports", plus={"account_asset", "account_saft"})

    util.rename_module(cr, "crm_iap_lead_enrich", "crm_iap_enrich")
    util.rename_module(cr, "crm_iap_lead", "crm_iap_mine")
    util.rename_module(cr, "crm_iap_lead_website", "website_crm_iap_reveal")

    util.new_module(cr, "project_mail_plugin", deps={"project", "mail_plugin"}, auto_install=True)
    util.new_module(cr, "hr_holidays_attendance", deps={"hr_holidays", "hr_attendance"}, auto_install=True)
    util.new_module(cr, "mail_group", deps={"mail", "portal"})

    if util.table_exists(cr, "mail_channel"):
        # Install the new mail_group module if there's some "mail_channel" with "email_send=True" in the database
        cr.execute("SELECT 1 FROM mail_channel WHERE email_send=TRUE FETCH FIRST ROW ONLY")
        if cr.rowcount:
            util.force_install_module(cr, "mail_group")
            util.force_migration_of_fresh_module(cr, "mail_group")
    util.new_module(cr, "website_mail_group", deps={"mail_group", "website"}, auto_install=True)

    util.merge_module(cr, "website_form", "website")
    util.merge_module(cr, "website_animate", "website")
    util.module_deps_diff(cr, "website", plus={"mail", "google_recaptcha", "utm"})
    util.module_deps_diff(cr, "website_crm_iap_reveal", minus={"crm_iap_mine"})

    util.new_module(
        cr,
        "website_sale_comparison_wishlist",
        deps={"website_sale_comparison", "website_sale_wishlist"},
        auto_install=True,
    )
    util.new_module(
        cr,
        "website_sale_stock_wishlist",
        deps={"website_sale_stock", "website_sale_wishlist"},
        auto_install=True,
    )

    util.new_module(cr, "project_mrp", deps={"mrp_account", "project"}, auto_install=True)
    util.new_module(cr, "project_purchase", deps={"purchase", "project"}, auto_install=True)

    util.module_deps_diff(cr, "project_timesheet_forecast", plus={"timesheet_grid"}, minus={"hr_timesheet"})
    util.module_deps_diff(cr, "auth_totp", plus={"mail"})

    util.new_module(cr, "pos_sale_product_configurator", deps={"point_of_sale", "sale_product_configurator"}, auto_install=True)
