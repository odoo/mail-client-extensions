# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_module(cr, "im_support")
    util.remove_module(cr, "odoo_referral_portal")

    # accounting modules
    util.merge_module(cr, "account_analytic_default", "account")
    util.merge_module(cr, "account_analytic_default_hr_expense", "hr_expense")
    util.merge_module(cr, "account_analytic_default_purchase", "purchase")
    util.new_module(cr, "account_edi", deps={"account"}, auto_install=True)
    util.new_module(cr, "account_edi_ubl", deps={"account_edi"}, auto_install=True)
    util.rename_module(cr, "account_facturx", "account_edi_facturx")
    util.module_deps_diff(cr, "account_edi_facturx", plus={"account_edi"}, minus={"account"})
    util.module_deps_diff(cr, "l10n_be_edi", minus={"account", "account_edi_facturx"}, plus={"account_edi"})
    util.module_deps_diff(cr, "l10n_it_edi", plus={"account_edi"})
    util.module_deps_diff(cr, "l10n_in", plus={"base_vat"})
    util.module_deps_diff(cr, "l10n_vn", plus={"l10n_multilang"})

    # Extracting coupon module from sale_coupon module
    util.new_module(cr, "coupon", deps={"account"})
    util.module_deps_diff(cr, "sale_coupon", plus={"coupon"})
    util.force_migration_of_fresh_module(cr, "coupon", init=True)

    # new event_crm module and its bridges
    util.new_module(cr, "event_crm", deps={"event", "crm"}, auto_install=True)
    util.new_module(cr, "event_crm_sale", deps={"event_crm", "event_sale"}, auto_install=True)
    util.new_module(cr, "website_event_crm", deps={"event_crm", "website_event"}, auto_install=True)
    util.new_module(
        cr, "website_event_crm_questions", deps={"website_event_crm", "website_event_questions"}, auto_install=True
    )

    util.new_module(cr, "google_recaptcha", deps={"base_setup"}, auto_install=True)
    util.new_module(cr, "mail_bot_hr", deps={"mail_bot", "hr"}, auto_install=True)
    util.module_deps_diff(cr, "crm_iap_lead", plus={"partner_autocomplete"})
    util.module_deps_diff(cr, "crm_iap_lead_enrich", plus={"partner_autocomplete"})
    util.module_deps_diff(cr, "mass_mailing", plus={"web_tour", "digest"})
    util.module_deps_diff(cr, "hr", minus={"mail_bot"})
    util.module_deps_diff(cr, "hr_timesheet", minus={"timer"})
    util.module_deps_diff(cr, "stock", plus={"digest"})
    util.module_deps_diff(cr, "website", plus={"digest"})
    util.module_deps_diff(cr, "website_form", plus={"google_recaptcha"})

    if not util.version_gte("saas~13.5"):
        # module already gone in saas~13.5 ¯\_(ツ)_/¯
        util.new_module(cr, "website_project", deps={"website", "project"}, auto_install=True)
        util.force_migration_of_fresh_module(cr, "website_project")

    # test modules
    util.module_deps_diff(
        cr,
        "test_event_full",
        plus={"event", "event_crm", "event_sale", "website_event_crm_questions", "website_event_track"},
    )
    util.module_deps_diff(cr, "test_mail", minus={"mail_bot"})
    util.new_module(cr, "test_search_panel", deps={"web"})

    if not util.module_installed(cr, "website"):
        util.remove_module(cr, "theme_bootswatch")

    if util.has_enterprise():
        util.new_module(cr, "data_cleaning", deps={"web", "mail", "phone_validation"})
        util.module_deps_diff(cr, "data_merge", plus={"data_cleaning"}, minus={"web"})
        util.module_auto_install(cr, "data_merge", True)

        util.new_module(cr, "digest_enterprise", deps={"web_enterprise", "digest"}, auto_install=True)
        util.new_module(cr, "documents_spreadsheet", deps={"documents"}, auto_install=True)
        util.new_module(cr, "hr_appraisal_survey", deps={"hr_appraisal", "survey"})
        util.new_module(cr, "hr_mobile", deps={"hr", "web_mobile"}, auto_install=True)
        util.new_module(cr, "l10n_au_reports", deps={"l10n_au", "account_reports_cash_basis"}, auto_install=True)

        util.module_deps_diff(cr, "account_consolidation", plus={"web_grid"})
        util.module_deps_diff(cr, "documents", plus={"digest"})
        util.module_deps_diff(cr, "helpdesk_timesheet", minus={"project_enterprise", "timer"}, plus={"timesheet_grid"})
        util.module_deps_diff(cr, "l10n_mx_edi", plus={"product_unspsc"})
        util.module_deps_diff(cr, "planning", plus={"digest"})
        util.module_deps_diff(cr, "project_forecast", plus={"web_grid"})
        util.module_deps_diff(cr, "snailmail_account_followup", plus={"snailmail_account"}, minus={"snailmail"})
        util.module_deps_diff(cr, "timesheet_grid", plus={"timer"})
        util.module_auto_install(cr, "timesheet_grid", {"web_grid", "hr_timesheet"})
        util.module_deps_diff(cr, "voip", plus={"web_mobile"})

        # test modules
        util.new_module(cr, "test_data_cleaning", deps={"data_cleaning"})
        util.module_deps_diff(cr, "test_mail_enterprise", plus={"marketing_automation_sms"})
        util.module_deps_diff(
            cr,
            "test_marketing_automation",
            plus={"marketing_automation_sms", "test_mass_mailing", "test_mail_enterprise", "test_mail_full"},
        )
    else:
        # moved to enterprise
        util.remove_module(cr, "test_timer")
        # `timer` module will be removed at the end to allow other modules to remove the mixin from their models.
        # Do not try to load it.
        cr.execute("UPDATE ir_module_module SET state='uninstalled' WHERE name='timer'")
