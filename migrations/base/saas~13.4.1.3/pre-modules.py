# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_module(cr, "odoo_referral_portal")
    util.remove_module(cr, "im_support")

    util.new_module_dep(cr, "crm_iap_lead", "partner_autocomplete")
    util.new_module_dep(cr, "crm_iap_lead_enrich", "partner_autocomplete")
    util.new_module(cr, "mail_bot_hr", deps={"mail_bot", "hr"}, auto_install=True)
    util.module_deps_diff(cr, "mass_mailing", plus={"web_tour"})
    util.module_deps_diff(cr, "hr", minus={"mail_bot"})
    util.module_deps_diff(cr, "test_mail", minus={"mail_bot"})
    util.new_module_dep(cr, "l10n_in", "base_vat")
    util.new_module(cr, "website_project", deps={"website", "project"}, auto_install=True)
    util.force_migration_of_fresh_module(cr, "website_project")
    # Extracting coupon module from sale_coupon module
    util.new_module(cr, "coupon", deps={"account"})
    util.module_deps_diff(cr, "sale_coupon", plus={"coupon"})
    util.force_migration_of_fresh_module(cr, "coupon", init=True)
    util.merge_module(cr, "account_analytic_default", "account")
    util.merge_module(cr, "account_analytic_default_hr_expense", "hr_expense")
    util.merge_module(cr, "account_analytic_default_purchase", "purchase")
    util.new_module(cr, "account_edi", deps={"account"}, auto_install=True)
    util.rename_module(cr, "account_facturx", "account_edi_facturx")
    util.module_deps_diff(cr, "account_edi_facturx", plus={"account_edi"}, minus={"account"})
    util.new_module(cr, "account_edi_ubl", deps={"account_edi"}, auto_install=True)
    util.module_deps_diff(cr, "l10n_be_edi", minus={"account", "account_edi_facturx"}, plus={"account_edi"})
    util.module_deps_diff(cr, "l10n_it_edi", plus={"account_edi"})
    util.module_deps_diff(cr, "l10n_be_edi", plus={"account_edi"})
    # new event_crm module and its bridges
    util.new_module(cr, "event_crm", deps={"event", "crm"}, auto_install=True)
    util.new_module(cr, "event_crm_sale", deps={"event_crm", "event_sale"}, auto_install=True)
    util.new_module(cr, "website_event_crm", deps={"event_crm", "website_event"}, auto_install=True)
    util.new_module(
        cr, "website_event_crm_questions", deps={"website_event_crm", "website_event_questions"}, auto_install=True
    )
    util.new_module(
        cr,
        "test_event_full",
        deps={
            "event",
            "event_crm",
            "event_sale",
            "website_event_crm_questions",
            "website_event_questions",
            "website_event_sale",
            "website_event_track",
        },
    )
    util.module_deps_diff(cr, "mass_mailing", plus={"digest"})
    util.module_deps_diff(cr, "hr_timesheet", minus={"timer"})

    if util.has_enterprise():
        util.new_module_dep(cr, "l10n_mx_edi", "product_unspsc")
        util.module_deps_diff(cr, "test_mail_enterprise", plus={"marketing_automation_sms"})
        util.module_deps_diff(
            cr,
            "test_marketing_automation",
            plus={"marketing_automation_sms", "test_mass_mailing", "test_mail_enterprise", "test_mail_full"},
        )
        util.new_module_dep(cr, "voip", "web_mobile")
        util.new_module(cr, "hr_appraisal_survey", deps={"hr_appraisal", "survey"})
        util.module_deps_diff(cr, "snailmail_account_followup", plus={"snailmail_account"}, minus={"snailmail"})
        util.module_deps_diff(cr, "timesheet_grid", plus={"timer"})
        util.module_deps_diff(cr, "helpdesk_timesheet", minus={"timer"}, plus={"timesheet_grid"})
        util.module_auto_install(cr, "timesheet_grid", {"web_grid", "hr_timesheet"})
    else:
        util.remove_module(cr, "timer")
        util.remove_module(cr, "test_timer")
