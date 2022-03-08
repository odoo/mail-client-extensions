# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):

    # saas specific. uninstall non-compatible module
    # this is safe as this module only contains model overwrites.
    cr.execute("UPDATE ir_module_module SET state='uninstalled' WHERE name='saas_pos_fast_reconcile'")

    # saas specific, no longer needed since firecloud saas credentials are now hosted on iap
    # and the ocn_client module (auto install) handles it customer-side
    # since the mail_push dep does not exist anymore, leaving it installed prevent updating saas_trial
    util.remove_module(cr, "saas_fcm")

    util.new_module(cr, "account_facturx", deps={"account"}, auto_install=True)
    util.new_module(cr, "auth_password_policy", deps={"base_setup", "web"}, auto_install=False)
    util.new_module(cr, "auth_password_policy_signup", deps={"auth_password_policy", "auth_signup"}, auto_install=True)
    util.new_module(cr, "crm_reveal", deps={"iap", "crm", "website_form"})
    util.new_module(cr, "delivery_hs_code", deps={"delivery"}, auto_install=True)
    util.new_module(cr, "hw_drivers")
    util.new_module(cr, "mail_bot", deps={"mail"}, auto_install=True)
    util.force_migration_of_fresh_module(cr, "mail_bot")
    util.new_module(cr, "im_livechat_mail_bot", deps={"im_livechat", "mail_bot"}, auto_install=True)
    util.new_module(cr, "mass_mailing_crm", deps={"mass_mailing", "crm"}, auto_install=True)
    util.new_module(
        cr, "mass_mailing_sale", deps={"mass_mailing", "sale", "website_sale_link_tracker"}, auto_install=True
    )
    util.new_module(cr, "sale_purchase", deps={"sale", "purchase"}, auto_install=True)
    util.force_migration_of_fresh_module(cr, "sale_purchase")
    util.new_module(cr, "snailmail", deps={"iap", "mail"}, auto_install=True)
    util.new_module(cr, "snailmail_account", deps={"snailmail", "account"}, auto_install=True)
    util.new_module(cr, "stock_zebra", deps={"base", "web", "stock"})
    util.new_module(cr, "web_unsplash", deps={"base_setup", "web_editor"}, auto_install=True)
    util.rename_module(cr, "website_quote", "sale_quotation_builder")
    util.module_deps_diff(cr, "sale_quotation_builder", minus={"mail", "sale_payment"})
    util.new_module(cr, "partner_autocomplete", deps={"web", "mail", "iap"})
    util.new_module(
        cr,
        "partner_autocomplete_address_extended",
        deps={"partner_autocomplete", "base_address_extended"},
        auto_install=True,
    )
    util.merge_module(cr, "base_vat_autocomplete", "partner_autocomplete")

    util.new_module(cr, "digest", deps={"mail", "portal"})
    for mod in "account crm hr_recruitment point_of_sale project sale_management website_sale".split():
        util.new_module_dep(cr, mod, "digest")

    util.new_module_dep(cr, "analytic", "uom")
    util.new_module_dep(cr, "contacts", "mail")
    util.new_module_dep(cr, "hr_timesheet", "uom")
    util.new_module_dep(cr, "l10n_be_invoice_bba", "l10n_be")
    util.new_module(cr, "l10n_cn_city", deps={"base_address_city", "l10n_cn"})
    util.module_deps_diff(cr, "lunch", plus={"mail"}, minus={"base", "web"})
    util.new_module_dep(cr, "mass_mailing", "contacts")
    util.module_deps_diff(cr, "project", minus={"product"})

    util.module_deps_diff(cr, "sale", plus={"payment"}, minus={"account"})
    util.module_deps_diff(cr, "sale_management", minus={"account_invoicing"})
    util.merge_module(cr, "sale_payment", "sale")
    util.module_deps_diff(cr, "sale_stock", plus={"sale"}, minus={"sale_management"})
    # TODO ensure `sale_payment` migration script are run before sale...

    util.module_deps_diff(cr, "stock_dropshipping", plus={"sale_purchase"})
    util.new_module_dep(cr, "test_mail", "mail_bot")
    util.new_module_dep(cr, "theme_bootswatch", "website_theme_install")
    util.new_module_dep(cr, "theme_default", "website_theme_install")

    if util.module_installed(cr, "sale"):
        util.move_field_to_module(cr, "sale.order", "commitment_date", "sale_order_dates", "sale")
        util.move_field_to_module(cr, "sale.order", "expected_date", "sale_order_dates", "sale")
    if util.module_installed(cr, "sale_stock"):
        util.move_field_to_module(cr, "sale.order", "effective_date", "sale_order_dates", "sale_stock")

    util.merge_module(cr, "account_invoicing", "account")
    util.merge_module(cr, "sale_order_dates", "sale")
    util.merge_module(cr, "website_sale_options", "website_sale")
    util.merge_module(cr, "website_sale_stock_options", "website_sale_stock")

    # force auto_install
    if util.modules_installed(cr, "website_sale", "sale_stock"):
        util.force_install_module(cr, "website_sale_stock")
        if util.modules_installed(cr, "delivery"):
            util.force_migration_of_fresh_module(cr, "website_sale_delivery")

    if util.has_enterprise():
        util.rename_module(cr, "report_intrastat", "account_intrastat")
        util.module_deps_diff(cr, "l10n_be_intrastat", minus={"sale_stock", "account"})
    else:
        # these modules have been moved to enterprise
        util.remove_module(cr, "report_intrastat")
        util.remove_module(cr, "l10n_be_intrastat")
        util.remove_module(cr, "account_asset")
        util.remove_module(cr, "account_budget")

    util.remove_module(cr, "anonymization")
    util.remove_module(cr, "website_forum_doc")

    if util.has_enterprise():
        util.rename_module(cr, "account_batch_deposit", "account_batch_payment")
        util.module_deps_diff(cr, "account_batch_payment", plus={"account"}, minus={"account_accountant"})
        util.rename_module(cr, "website_sign", "sign")
        util.rename_module(cr, "mail_push", "ocn_client")
        if util.module_installed(cr, "web_clearbit"):
            util.force_install_module(cr, "partner_autocomplete")
        util.merge_module(cr, "web_clearbit", "partner_autocomplete")

        util.new_module(
            cr, "account_invoice_extract", deps={"account_accountant", "iap", "mail_enterprise"}, auto_install=True
        )
        util.force_migration_of_fresh_module(cr, "account_invoice_extract")
        util.new_module(
            cr, "account_invoice_extract_purchase", deps={"account_invoice_extract", "purchase"}, auto_install=True
        )
        util.new_module(cr, "account_predictive_bills", deps={"account_accountant"}, auto_install=True)
        util.new_module(cr, "crm_enterprise", deps={"crm", "web_dashboard", "web_cohort"}, auto_install=True)
        util.force_migration_of_fresh_module(cr, "crm_enterprise")
        util.new_module(cr, "iot", deps={"web"})
        util.new_module(cr, "documents", deps={"base", "mail", "portal", "web"})
        for mod in {"account", "product", "project", "sign"}:
            util.new_module(cr, "documents_" + mod, deps={"documents", mod}, auto_install=True)
        util.new_module(cr, "event_enterprise", deps={"event", "web_cohort"}, auto_install=True)
        util.force_migration_of_fresh_module(cr, "event_enterprise")
        util.new_module(cr, "l10n_au_aba", deps={"account_batch_payment", "l10n_au"}, auto_install=True)
        util.new_module(cr, "l10n_co_edi", deps={"account", "l10n_co"})
        util.new_module(cr, "l10n_es_real_estates", deps={"l10n_es_reports"})
        util.new_module(cr, "l10n_es_reports_2021", deps={"l10n_es_reports"}, auto_install=True)
        util.new_module(cr, "l10n_nl_intrastat", deps={"l10n_nl", "account_intrastat"}, auto_install=True)
        util.new_module(
            cr,
            "purchase_mrp_workorder_quality",
            deps={"purchase_mrp", "quality_mrp_workorder", "purchase_stock"},
            auto_install=True,
        )
        util.new_module(cr, "pos_iot", deps={"point_of_sale", "iot"}, auto_install=True)
        util.new_module(cr, "pos_restaurant_iot", deps={"pos_restaurant", "iot"}, auto_install=True)
        util.new_module(cr, "quality_iot", deps={"iot", "quality_control"}, auto_install=True)
        util.new_module(cr, "quality_mrp_iot", deps={"iot", "quality_mrp_workorder"}, auto_install=True)
        util.new_module(cr, "mrp_zebra", deps={"stock_zebra", "quality_mrp_iot"})
        util.new_module(cr, "sale_enterprise", deps={"sale", "web_dashboard"}, auto_install=True)
        util.new_module(
            cr, "snailmail_account_reports_followup", deps={"snailmail", "account_reports_followup"}, auto_install=True
        )
        util.new_module(cr, "stock_account_enterprise", deps={"stock_account", "web_dashboard"}, auto_install=True)
        util.new_module(cr, "stock_enterprise", deps={"stock", "web_dashboard", "web_cohort"}, auto_install=True)
        util.new_module(cr, "stock_intrastat", deps={"stock_account", "account_intrastat"}, auto_install=True)
        util.new_module(cr, "website_twitter_wall", deps={"website_twitter"})

        util.module_deps_diff(
            cr,
            "account_intrastat",
            plus={"account_reports"},
            minus={"base", "product", "delivery", "stock", "sale_management", "purchase"},
        )
        if util.module_installed(cr, "account_intrastat"):
            util.force_install_module(cr, "stock_intrastat")

        # One app free should remain one app free
        if util.module_installed(cr, "account_reports"):
            cr.execute(
                """
                SELECT COUNT(*)
                  FROM ir_module_module_dependency d
            INNER JOIN ir_module_module m ON d.module_id = m.id
                 WHERE d.name = 'account_reports'
                   AND m.state IN %s
            """,
                [util.INSTALLED_MODULE_STATES],
            )
            if not cr.fetchone()[0]:
                util.uninstall_module(cr, "account_reports")

        util.module_deps_diff(cr, "account_accountant", minus={"account_reports"})
        util.module_deps_diff(cr, "account_reports", plus={"account_accountant"}, minus={"account"})
        util.module_deps_diff(cr, "account_sepa", plus={"account_batch_payment"}, minus={"account"})
        util.module_deps_diff(cr, "account_sepa_direct_debit", plus={"account_batch_payment"}, minus={"account"})
        util.module_deps_diff(cr, "helpdesk", plus={"digest"})
        util.module_deps_diff(cr, "inter_company_rules", minus={"sale"})  # from merge of sale_order_dates
        util.module_deps_diff(cr, "l10n_mx_edi_landing", minus={"account_accountant"})
        util.module_deps_diff(cr, "mrp_account", plus={"stock_account"}, minus={"account"})
        util.module_deps_diff(cr, "ocn_client", plus={"iap"}, minus={"web_mobile"})
        util.module_deps_diff(
            cr,
            "sale_subscription",
            plus={"account_deferred_revenue", "rating", "base_automation"},
            minus={"sale"},  # actually minus=sale_payment, but has been merged and deps updated
        )
        util.module_deps_diff(
            cr, "sale_subscription_dashboard", plus={"sale_subscription"}, minus={"account_deferred_revenue"}
        )
        if util.modules_installed(cr, "sale_subscription", "sale_subscription_asset"):
            util.force_install_module(cr, "sale_subscription_dashboard")

        util.module_deps_diff(cr, "sign", plus={"sms"})
        util.module_deps_diff(cr, "website_calendar", plus={"website_enterprise"}, minus={"website"})
        util.module_deps_diff(cr, "website_crm_score", plus={"crm_enterprise"})

        util.remove_module(cr, "account_extension")
        # Move field info to hr_expense module. We don't care about data of this transient model.
        # This will avoid useless warning about respawn field
        util.move_field_to_module(
            cr,
            "hr.expense.sheet.register.payment.wizard",
            "partner_bank_account_id",
            "hr_expense_sepa",
            "hr_expense",
        )
        util.remove_module(cr, "hr_expense_sepa")
        util.remove_module(cr, "print_sale")
        util.remove_module(cr, "print")
        util.remove_module(cr, "print_docsaway")
        util.remove_module(cr, "website_quote_subscription")
        util.remove_module(cr, "website_sale_dashboard_with_margin")
        util.remove_module(cr, "website_version")  # merged into website?

    if util.has_design_themes():
        util.merge_module(cr, "snippet_latest_posts", "website_blog", update_dependers=False)
        util.merge_module(cr, "snippet_google_map", "theme_common", update_dependers=False)
        util.module_deps_diff(cr, "theme_treehouse", plus={"theme_common"})

        util.module_deps_diff(cr, "theme_common", plus={"website_theme_install"})
