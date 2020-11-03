# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.new_module(cr, "auth_password_policy_portal", deps={"auth_password_policy", "portal"}, auto_install=True)
    util.new_module(cr, "auth_totp", deps={"web"}, auto_install=True)
    util.new_module(cr, "auth_totp_portal", deps={"portal", "auth_totp"}, auto_install=True)
    util.new_module(cr, "mail_client_extension", deps={"web", "crm", "crm_iap_lead_enrich"})
    util.new_module(cr, "test_apikeys", deps={"web_tour"})
    util.new_module(cr, "test_auth_custom", deps={})

    util.module_auto_install(cr, "mail_bot", auto_install=True)

    if util.has_enterprise():
        util.new_module(cr, "documents_spreadsheet_account", deps={"documents_spreadsheet", "account"}, auto_install=True)
        util.new_module(cr, "documents_spreadsheet_crm", deps={"documents_spreadsheet", "crm"}, auto_install=True)
        util.module_deps_diff(cr, "event_barcode_mobile", plus={"barcodes_mobile"}, minus={"web_mobile"})
        util.new_module(cr, "hr_attendance_mobile", deps={"hr_attendance", "barcodes_mobile"}, auto_install=True)
        util.new_module(cr, "hr_gantt", deps={"hr", "web_gantt"}, auto_install=True)
        util.module_deps_diff(cr, "planning", plus={"hr_gantt"})
        util.new_module(cr, "pos_hr_mobile", deps={"pos_hr", "web_mobile"}, auto_install=True)
        util.module_auto_install(cr, "pos_loyalty", auto_install=True)

    util.remove_module(cr, "hw_proxy")
    util.remove_module(cr, "pos_reprint")

    if util.has_enterprise():
        util.new_module(
            cr, "crm_enterprise_iap_lead_website",
            deps={"crm_enterprise", "crm_iap_lead_website"},
            auto_install=True
        )
        util.new_module(
            cr, "crm_enterprise_partner_assign",
            deps={"crm_enterprise", "website_crm_partner_assign"},
            auto_install=True
        )
        util.merge_module(cr, "iot_pairing", "iot")
        util.merge_module(cr, 'l10n_co_edi_ubl_2_1', 'l10n_co_edi')
        util.module_deps_diff(cr, 'l10n_co_edi', plus={'product_unspsc'})

    util.module_deps_diff(cr, 'l10n_co', plus={'base_address_city', 'account_debit_note', 'l10n_latam_base'})

    util.new_module(cr, "iap_mail", deps={"iap", "mail"}, auto_install=True)
    util.new_module(cr, "iap_crm", deps={"crm", "iap_mail"}, auto_install=True)
    util.new_module(cr, "microsoft_account", deps={"base_setup"})
    util.new_module(cr, "microsoft_calendar", deps={"microsoft_account", "calendar"})

    util.module_deps_diff(cr, "crm_iap_lead",
                          plus={"iap_crm", "iap_mail"},
                          minus={"iap", "crm", "partner_autocomplete"})
    util.module_deps_diff(cr, "crm_iap_lead_enrich",
                          plus={"iap_crm", "iap_mail"},
                          minus={"iap", "crm", "partner_autocomplete"})
    util.module_deps_diff(cr, "crm_iap_lead_website",
                          plus={"iap_crm", "iap_mail"},
                          minus={"iap", "crm"})
    util.module_deps_diff(cr, "l10n_ec",
                          plus={"l10n_latam_invoice_document", "l10n_latam_base"})
    util.module_deps_diff(cr, 'l10n_latam_invoice_document',
                          plus={'account_debit_note'})
    util.module_deps_diff(cr, "partner_autocomplete",
                          plus={"iap_mail"},
                          minus={"iap", "mail", "web"})
    util.module_deps_diff(cr, "sms",
                          plus={"iap_mail"},
                          minus={"iap"})
    util.module_deps_diff(cr, "snailmail",
                          plus={"iap_mail"},
                          minus={"iap"})
    util.module_deps_diff(cr, "test_event_full",
                          minus={"website_event_track_online", "website_event_track_session", "website_event_online"})
    util.module_deps_diff(cr, "website_event_meet",
                          plus={"website_event"},
                          minus={"website_event_track_online", "website_event_online"})
    util.module_deps_diff(cr, "website_event_track_exhibitor",
                          plus={"website_event_track"},
                          minus={"website_event_track_online"})
    util.module_deps_diff(cr, "website_event_track_live",
                          plus={"website_event_track"},
                          minus={"website_event_track_online", "website_event_track_session"})
    util.module_deps_diff(cr, "website_event_track_quiz",
                          plus={"website_event_track"},
                          minus={"website_event_track_session"})

    # website_event_*_online modules are manually merged in `pre-30-*` scripts

    util.remove_module(cr, 'hr_expense_check')
    util.remove_module(cr, 'website_project')

    if util.has_enterprise():
        util.module_deps_diff(cr, 'l10n_ar_edi',
                              minus={'account_debit_note'})
        util.module_deps_diff(cr, "mail_mobile",
                              plus={"iap_mail"},
                              minus={"iap"})
        util.module_deps_diff(cr, "website_event_social",
                              plus={"website_event"},
                              minus={"website_event_online"})
        util.module_deps_diff(cr, "website_event_track_social",
                              plus={"website_event_track_session"},
                              minus={"website_event_track"})
        util.module_deps_diff(cr, "website_event_twitter_wall",
                              plus={"website_event"},
                              minus={"website_event_track_online"})

        util.module_auto_install(cr, "website_event_social", True)
        util.module_auto_install(cr, "website_event_track_social", True)
        util.module_auto_install(cr, "website_event_twitter_wall", True)

        util.merge_module(cr, "sale_amazon_authentication", "sale_amazon")

    util.force_migration_of_fresh_module(cr, "iap_mail")
    util.force_migration_of_fresh_module(cr, "iap_crm")

    util.new_module(cr, "pos_restaurant_adyen", deps={"pos_adyen", "pos_restaurant", "payment_adyen"}, auto_install=True)

    # ===========================================================
    # account_edi + refactoring l10n_mx_edi (PR: 52407 & 12226)
    # ===========================================================

    if util.has_enterprise():
        # l10n_mx_edi splitted into two modules: l10n_mx_edi & l10n_mx_edi_extended
        util.module_deps_diff(cr, 'l10n_mx_edi', plus={'account_edi', 'l10n_mx'}, minus={'account'})
        util.new_module(cr, 'l10n_mx_edi_extended', deps={'l10n_mx_edi'})
        util.module_deps_diff(cr, "l10n_mx_edi_landing", plus={"l10n_mx_edi_extended"}, minus={"l10n_mx_edi"})
        if util.module_installed(cr, 'l10n_mx_edi'):
            util.force_install_module(cr, 'l10n_mx_edi_extended')

    # ===========================================================
    # Add account_disallowed_expenses (PR: 49675 & 8480)
    # ===========================================================

    util.rename_module(cr, 'fleet_account', 'account_fleet')
    if util.has_enterprise():
        util.new_module(cr, 'account_disallowed_expenses', deps={'account_reports'})
        util.new_module(cr, 'account_disallowed_expenses_fleet', deps={'account_disallowed_expenses', 'account_fleet'}, auto_install=True)
        util.new_module(cr, 'l10n_be_disallowed_expenses', deps={'account_disallowed_expenses', 'l10n_be'}, auto_install=True)

    # account_edi add a new field on account_move and bootstrap it using SQL instead of letting
    # the ORM compute it slowly
    util.force_migration_of_fresh_module(cr, "account_edi")
