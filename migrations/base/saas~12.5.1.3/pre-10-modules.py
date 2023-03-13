# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.new_module(cr, "crm_iap_lead_enrich", deps={"iap", "crm"})
    util.new_module(cr, "crm_sms", deps={"crm", "sms"}, auto_install=True)
    util.new_module(cr, "event_sms", deps={"event", "sms"}, auto_install=True)
    util.new_module(cr, "stock_sms", deps={"stock", "sms"}, auto_install=True)

    util.new_module(cr, "hr_holidays_attendance", deps={"hr_attendance", "hr_holidays"}, auto_install=True)
    util.new_module(cr, "hr_work_entry", deps={"hr"})
    if util.module_installed(cr, "hr"):
        util.force_install_module(cr, "hr_work_entry")
        util.force_migration_of_fresh_module(cr, "hr_work_entry")

    util.new_module(cr, "l10n_latam_base", deps={"base_vat", "contacts"})
    util.new_module(cr, "l10n_latam_invoice_document", deps={"account"})
    util.new_module(cr, "l10n_in_purchase_stock", deps={"l10n_in_purchase", "l10n_in_stock"}, auto_install=True)
    util.new_module(cr, "l10n_in_sale_stock", deps={"l10n_in_sale", "l10n_in_stock"}, auto_install=True)

    util.new_module(cr, "mass_mailing_sms", deps={"portal", "mass_mailing", "sms"})
    util.new_module(
        cr, "mass_mailing_event_sms", deps={"event", "mass_mailing", "mass_mailing_sms", "sms"}, auto_install=True
    )
    util.new_module(
        cr,
        "mass_mailing_event_track_sms",
        deps={"mass_mailing", "mass_mailing_sms", "sms", "website_event_track"},
        auto_install=True,
    )
    util.new_module(cr, "mass_mailing_slides", deps={"website_slides", "mass_mailing"}, auto_install=True)

    util.new_module(cr, "mrp_subcontracting", deps={"mrp"})
    util.new_module(cr, "mrp_subcontracting_account", deps={"mrp_subcontracting", "mrp_account"}, auto_install=True)
    util.new_module(
        cr, "mrp_subcontracting_dropshipping", deps={"mrp_subcontracting", "stock_dropshipping"}, auto_install=True
    )

    # util.new_module(cr, "payment_test", deps={"payment"})
    util.new_module(cr, "pos_adyen", deps={"point_of_sale"})
    util.new_module(cr, "pos_epson_printer", deps={"point_of_sale"})
    util.new_module(cr, "pos_epson_printer_restaurant", deps={"pos_epson_printer", "pos_restaurant"}, auto_install=True)

    util.new_module(cr, "product_matrix", deps={"account"})
    util.new_module(cr, "purchase_product_matrix", deps={"purchase", "product_matrix"})
    util.new_module(cr, "sale_product_matrix", deps={"sale", "product_matrix", "sale_product_configurator"})

    util.new_module(cr, "website_sms", deps={"website", "sms"}, auto_install=True)
    util.new_module(cr, "website_crm_livechat", deps={"website_crm", "website_livechat"}, auto_install=True)
    util.new_module(cr, "website_crm_sms", deps={"website_sms", "crm"}, auto_install=True)

    util.rename_module(cr, "payment_ogone", "payment_ingenico")

    util.module_deps_diff(cr, "base_iban", plus={"web"})
    util.module_deps_diff(cr, "hr", plus={"mail_bot"})
    util.module_deps_diff(cr, "iap", plus={"base_setup"}, minus={"web_settings_dashboard"})

    util.module_deps_diff(
        cr, "l10n_ar", plus={"l10n_latam_base", "l10n_latam_invoice_document"}, minus={"base", "account"}
    )
    util.module_deps_diff(cr, "l10n_at", plus={"base_iban", "base_vat"})
    util.module_deps_diff(
        cr,
        "l10n_cl",
        plus={"contacts", "base_address_city", "base_vat", "l10n_latam_base", "l10n_latam_invoice_document", "uom"},
        minus={"account"},
    )
    util.module_deps_diff(cr, "l10n_fr_pos_cert", plus={"l10n_fr"}, minus={"l10n_fr_sale_closing"})
    util.module_auto_install(cr, "l10n_fr_pos_cert", True)
    util.module_deps_diff(
        cr,
        "l10n_pe",
        plus={"base_vat", "base_address_extended", "base_address_city", "l10n_latam_base"},
        minus={"account"},
    )

    util.module_deps_diff(cr, "phone_validation", plus={"mail"})
    util.module_auto_install(cr, "phone_validation", True)
    util.module_deps_diff(cr, "resource", plus={"web"})
    util.module_deps_diff(cr, "sms", plus={"phone_validation"})
    util.module_deps_diff(cr, "survey", plus={"gamification"})
    util.module_deps_diff(cr, "utm", plus={"web"})
    util.module_deps_diff(cr, "website", plus={"auth_signup"})
    util.module_deps_diff(cr, "test_inherit", plus={"test_new_api"})

    util.module_auto_install(cr, "website_sale_slides", False)

    util.merge_module(cr, "decimal_precision", "base", update_dependers=False)
    util.merge_module(cr, "payment_stripe_sca", "payment_stripe")

    if util.module_installed(cr, "l10n_fr"):
        util.move_field_to_module(cr, "res.company", "l10n_fr_closing_sequence_id", "l10n_fr_sale_closing", "l10n_fr")

        if util.module_installed(cr, "l10n_fr_pos_cert"):
            util.remove_module_deps(cr, "l10n_fr_sale_closing", {"l10n_fr_certification"})
            util.merge_module(cr, "l10n_fr_sale_closing", "l10n_fr_pos_cert")
        else:
            util.remove_module(cr, "l10n_fr_sale_closing")

    if not util.module_installed(cr, "account"):
        # account will steal fields before removing the module
        util.remove_module(cr, "l10n_fr_certification")

    if util.has_enterprise():
        util.module_auto_install(cr, "account_asset", True)
        util.module_auto_install(cr, "account_bank_statement_import_camt", True)

        util.rename_module(cr, "hr_documents", "documents_hr")  # Marvelous!

        # The `sale_rental` module create a name conflict with one module of OCA [1] and has thus been renamed in saas~12.5.
        # We rename the existing modules if the source version is saas~12.4, else we create them with the right name.
        # [1] https://twitter.com/PedroMBaeza/status/1151530523807891456
        if version.startswith("saas~12.4."):
            util.rename_module(cr, "sale_rental", "sale_renting")
            util.rename_module(cr, "sale_rental_sign", "sale_renting_sign")
            util.rename_module(cr, "sale_stock_rental", "sale_stock_renting")
        else:
            util.new_module(cr, "sale_renting", deps={"sale"})
            util.new_module(cr, "sale_renting_sign", deps={"sign", "sale_renting"}, auto_install=True)
            util.new_module(cr, "sale_stock_renting", deps={"sale_renting", "sale_stock"}, auto_install=True)

        util.rename_module(cr, "snailmail_account_reports_followup", "snailmail_account_followup")

        util.new_module(cr, "account_auto_transfer", deps={"account_accountant"}, auto_install=True)
        util.new_module(cr, "account_consolidation", deps={"account_reports"})
        util.new_module(cr, "account_winbooks_import", deps={"account_accountant", "base_vat"})

        util.rename_module(cr, "map_view_contact", "contacts_enterprise")
        util.new_module(cr, "documents_fleet", deps={"documents", "fleet"}, auto_install=True)
        util.new_module(cr, "documents_hr_contract", deps={"documents_hr", "hr_contract"}, auto_install=True)
        util.force_migration_of_fresh_module(cr, "documents_hr_contract", init=False)
        util.new_module(cr, "documents_hr_holidays", deps={"documents_hr", "hr_holidays"}, auto_install=True)
        util.new_module(cr, "documents_hr_payroll", deps={"documents_hr", "hr_payroll"}, auto_install=True)
        util.force_migration_of_fresh_module(cr, "documents_hr_payroll", init=False)
        util.new_module(cr, "documents_hr_recruitment", deps={"documents_hr", "hr_recruitment"}, auto_install=True)
        util.new_module(cr, "helpdesk_fsm", deps={"helpdesk", "industry_fsm"}, auto_install=True)
        util.new_module(cr, "hr_contract_sign", deps={"hr_contract", "sign"}, auto_install=True)
        util.force_migration_of_fresh_module(cr, "hr_contract_sign")
        util.new_module(cr, "hr_payroll_account_sepa", deps={"hr_payroll_account", "account_sepa"})
        util.new_module(cr, "hr_payroll_expense", deps={"hr_payroll", "hr_expense"})
        util.new_module(
            cr, "hr_referral", deps={"hr_recruitment", "link_tracker", "website_hr_recruitment", "web_dashboard"}
        )

        util.new_module(cr, "l10n_ar_reports", deps={"l10n_ar", "account_reports"}, auto_install=True)
        util.new_module(
            cr, "l10n_at_reports", deps={"l10n_at", "account_reports", "account_accountant"}, auto_install=True
        )
        util.new_module(cr, "l10n_lu_reports", deps={"l10n_lu", "account_reports"}, auto_install=True)

        util.new_module(
            cr, "marketing_automation_sms", deps={"marketing_automation", "mass_mailing_sms"}, auto_install=True
        )
        util.new_module(cr, "payment_sepa_direct_debit", deps={"account_sepa_direct_debit", "payment", "sms"})
        util.new_module(cr, "planning", deps={"hr", "web_gantt"})
        util.new_module(cr, "sale_amazon", deps={"sale_management", "stock"})
        util.new_module(cr, "sale_amazon_delivery", deps={"sale_amazon", "delivery"}, auto_install=True)
        util.new_module(cr, "sale_amazon_taxcloud", deps={"sale_amazon", "account_taxcloud"}, auto_install=True)
        util.new_module(
            cr,
            "sale_subscription_sepa_direct_debit",
            deps={"sale_subscription", "payment_sepa_direct_debit"},
            auto_install=True,
        )
        util.new_module(cr, "social", deps={"web", "mail", "iap", "link_tracker"})
        util.new_module(cr, "social_crm", deps={"social", "crm"}, auto_install=True)
        util.new_module(cr, "social_facebook", deps={"social"}, auto_install=True)
        util.new_module(cr, "social_linkedin", deps={"social", "iap"}, auto_install=True)  # ?
        util.new_module(cr, "social_push_notifications", deps={"social", "website"}, auto_install=True)
        util.new_module(cr, "social_sale", deps={"social", "sale"}, auto_install=True)
        util.new_module(cr, "social_twitter", deps={"social", "iap"}, auto_install=True)
        util.new_module(cr, "website_event_track_gantt", deps={"website_event_track", "web_gantt"}, auto_install=True)

        # demo modules. They are actually auto_install, but we don't care installing them during upgrades
        util.new_module(
            cr,
            "l10n_be_us_consolidation_demo",
            deps={"account_consolidation", "l10n_be", "l10n_generic_coa"},
            auto_install=False,
        )
        util.new_module(
            cr,
            "l10n_generic_auto_transfer_demo",
            deps={"account_auto_transfer", "l10n_generic_coa"},
            auto_install=False,
        )

        util.rename_module(cr, "account_reports_followup", "account_followup")
        util.module_deps_diff(cr, "account_followup", plus={"sms"})
        util.module_auto_install(cr, "account_followup", True)

        util.module_deps_diff(cr, "hr_appraisal", plus={"web_gantt"})
        util.module_deps_diff(cr, "hr_payroll", plus={"hr_work_entry", "mail"})
        util.module_deps_diff(cr, "hr_payroll_account", plus={"account_accountant"}, minus={"account"})
        util.module_deps_diff(
            cr, "industry_fsm", plus={"sale_timesheet_enterprise"}, minus={"sale_project_timesheet_enterprise"}
        )
        util.module_deps_diff(cr, "l10n_be_hr_payroll_account", plus={"l10n_be"})
        util.module_deps_diff(cr, "project_enterprise", plus={"web_gantt"})
        util.module_deps_diff(cr, "project_forecast", plus={"planning"}, minus={"web_grid", "hr", "web_gantt"})
        util.force_migration_of_fresh_module(cr, "planning")
        util.module_deps_diff(cr, "sale_subscription", plus={"sms"})
        util.module_deps_diff(cr, "stock_enterprise", plus={"web_grid"})
        util.module_deps_diff(
            cr,
            "test_l10n_be_hr_payroll_account",
            plus={
                "hr_payroll_account_sepa",
                "documents_hr_payroll",
                "documents_hr_recruitment",
                "documents_hr_contract",
            },
        )
        util.module_deps_diff(cr, "web_map", plus={"base_setup"})
        util.force_migration_of_fresh_module(cr, "web_map")

        util.module_deps_diff(
            cr, "website_sale_account_taxcloud", plus={"sale_account_taxcloud"}, minus={"account_taxcloud"}
        )

        util.merge_module(cr, "account_deferred_revenue", "account_asset")
        util.merge_module(cr, "l10n_be_intrastat_2019", "l10n_be_intrastat")
        util.merge_module(cr, "l10n_mx_edi_cancellation", "l10n_mx_edi")
        util.merge_module(cr, "l10n_mx_edi_customs", "l10n_mx_edi")
        util.merge_module(cr, "l10n_mx_edi_external_trade", "l10n_mx_edi")
        util.merge_module(cr, "l10n_mx_edi_payment_bank", "l10n_mx_edi")
        util.merge_module(cr, "l10n_mx_tax_cash_basis", "l10n_mx_edi")

        eb = util.expand_braces
        if util.modules_installed(cr, *eb("sale_{project_,}timesheet_enterprise")):
            util.move_model(cr, "project.task.create.sale.order", *eb("sale_{project_,}timesheet_enterprise"))
        util.remove_module(cr, "sale_project_timesheet_enterprise")

    util.remove_module(cr, "account_cancel")
    util.remove_module(cr, "hr_attendance_presence")
    cr.execute("DELETE FROM ir_config_parameter WHERE key='hr_presence.hr_presence_control_attendance'")

    util.remove_module(cr, "hw_scale")
    util.remove_module(cr, "hw_scanner")
    util.remove_module(cr, "hw_screen")

    util.merge_module(cr, "l10n_in_schedule6", "l10n_in")

    util.remove_module(cr, "web_settings_dashboard")
    util.remove_module(cr, "website_crm_phone_validation")
    util.remove_module(cr, "website_hr")

    util.remove_module(cr, "test_pylint")
