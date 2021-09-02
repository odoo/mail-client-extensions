# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.module_deps_diff(cr, "event", plus={"utm"})
    util.module_deps_diff(cr, "link_tracker", plus={"mail"})
    util.new_module(cr, "mrp_landed_costs", deps={"stock_landed_costs", "mrp"}, auto_install=True)
    util.new_module(cr, "account_qr_code_sepa", deps={"account", "base_iban"}, auto_install=True)
    util.module_deps_diff(cr, "sale_coupon", plus={"sale"}, minus={"sale_management"})

    util.module_auto_install(cr, "crm_iap_lead", True)
    util.module_auto_install(cr, "crm_iap_lead_enrich", True)

    # new Event Online support
    util.new_module(cr, "website_jitsi", deps={"website"})
    util.new_module(cr, "website_event_online", deps={"website_event"})
    util.new_module(cr, "website_event_track_online", deps={"sms", "website_event_track", "website_event_online"})
    util.new_module(
        cr, "website_event_meet", deps={"website_event_online", "website_event_track_online", "website_jitsi"}
    )
    util.new_module(cr, "website_event_track_exhibitor", deps={"website_event_track_online", "website_jitsi"})
    util.new_module(cr, "website_event_track_session", deps={"website_event_track_online"})
    util.new_module(cr, "website_event_track_live", deps={"website_event_track_online", "website_event_track_session"})
    util.new_module(cr, "website_event_track_quiz", deps={"website_profile", "website_event_track_session"})
    util.new_module(cr, "website_event_track_live_quiz", deps={"website_event_track_live", "website_event_track_quiz"})
    util.new_module(cr, "website_event_meet_quiz", deps={"website_event_meet", "website_event_track_quiz"})

    util.new_module(
        cr,
        "test_event_full",
        deps={
            "website_event_online",
            "website_event_questions",
            "website_event_meet",
            "website_event_sale",
            "website_event_track_online",
            "website_event_track_exhibitor",
            "website_event_track_session",
            "website_event_track_live",
            "website_event_track_quiz",
        },
    )

    if util.has_enterprise():
        util.new_module(
            cr, "documents_l10n_be_hr_payroll", deps={"documents_hr_payroll", "l10n_be_hr_payroll"}, auto_install=True
        )
        util.new_module(cr, "hr_contract_salary_payroll", deps={"hr_contract_salary", "hr_payroll"}, auto_install=True)
        # https://github.com/odoo/enterprise/pull/11294
        util.new_module(cr, "purchase_intrastat", deps={"purchase", "account_intrastat"}, auto_install=True)
        util.new_module(
            cr, "purchase_stock_enterprise", deps={"purchase_enterprise", "purchase_stock"}, auto_install=True
        )
        util.new_module(cr, "sale_renting_crm", deps={"sale_renting", "crm"}, auto_install=True)

        util.new_module(
            cr,
            "l10n_be_hr_contract_salary",
            deps={"hr_contract_salary_payroll", "l10n_be_hr_payroll_fleet"},
            auto_install=True,
        )
        util.force_migration_of_fresh_module(cr, "l10n_be_hr_contract_salary")
        util.new_module(cr, "l10n_be_hr_payroll_posted_employee", deps={"l10n_be_hr_payroll"}, auto_install=True)

        util.module_deps_diff(
            cr,
            "hr_contract_salary",
            plus={"hr_contract_reports", "http_routing"},
            minus={"website", "l10n_be_hr_payroll_fleet"},
        )
        util.module_deps_diff(
            cr,
            "test_l10n_be_hr_payroll_account",
            plus={"hr_contract_salary_payroll", "l10n_be_hr_contract_salary"},
            minus={"hr_contract_salary"},
        )
        util.new_module(cr, "hr_payroll_edit_lines", deps={"hr_payroll"}, auto_install=True)
        util.new_module(cr, "l10n_be_hr_payroll_proration", deps={"l10n_be_hr_payroll"}, auto_install=True)

        util.merge_module(cr, "social_linkedin_company_support", "social_linkedin")

        # new Event Online support
        util.new_module(cr, "website_event_social", deps={"website_event_online", "social_push_notifications"})
        util.new_module(cr, "website_event_track_social", deps={"website_event_social", "website_event_track_session"})
        util.new_module(cr, "website_event_twitter_wall", deps={"website_twitter_wall", "website_event_track_online"})
