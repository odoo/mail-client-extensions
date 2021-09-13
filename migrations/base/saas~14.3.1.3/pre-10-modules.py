# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "account_edi_extended", "account_edi", update_dependers=False)
    util.merge_module(cr, "l10n_ch_qriban", "l10n_ch")

    util.new_module(cr, "account_edi_ubl_bis3", deps={"account_edi_ubl"})
    util.new_module(cr, "l10n_nl_edi", deps={"l10n_nl", "account_edi_ubl_bis3"}, auto_install=True)

    util.new_module(cr, "barcodes_gs1_nomenclature", deps={"barcodes", "uom"}, auto_install=False)

    util.new_module(cr, "gift_card", deps={"sale"})
    util.new_module(cr, "website_sale_gift_card", deps={"website_sale", "gift_card"})

    util.new_module(cr, "website_sale_blog", deps={"website_sale", "website_blog"}, auto_install=True)

    util.rename_module(cr, "payment_ingenico", "payment_ogone")
    util.rename_module(cr, "payment_odoo_by_adyen", "payment_odoo")

    util.module_deps_diff(cr, "l10n_it_edi_sdicoop", plus={"account_edi"})
    util.module_deps_diff(cr, "l10n_pe", plus={"l10n_latam_invoice_document", "account_debit_note"})

    util.remove_module_deps(cr, "website_hr_recruitment", {"website_partner"})
    util.module_auto_install(cr, "website_hr_recruitment", ["hr_recruitment", "website_mail"])

    util.module_deps_diff(cr, "mail_client_extension", minus={"crm", "crm_iap_lead_enrich"}, plus={"contacts", "iap"})
    util.rename_module(cr, "mail_client_extension", "mail_plugin")

    util.new_module(cr, "crm_mail_plugin", deps={"crm", "mail_plugin"}, auto_install=True)

    util.module_auto_install(cr, "website_payment", True)

    if util.has_enterprise():
        util.merge_module(cr, "account_reports_tax", "account_reports")
        util.merge_module(cr, "documents_l10n_be_hr_payroll_273S_274", "documents_l10n_be_hr_payroll")
        util.merge_module(cr, "l10n_be_hr_payroll_273S_274", "l10n_be_hr_payroll")
        util.merge_module(cr, "l10n_be_hr_payroll_273S_274_account", "l10n_be_hr_payroll_account")
        util.merge_module(cr, "l10n_be_hr_payroll_impulsion", "l10n_be_hr_payroll")
        util.merge_module(cr, "l10n_be_hr_payroll_onss_restructuring", "l10n_be_hr_payroll")

        util.new_module(cr, "helpdesk_mail_plugin", deps={"helpdesk", "mail_plugin"}, auto_install=True)
        util.new_module(cr, "hr_work_entry_contract_enterprise", deps={"hr_work_entry_contract"}, auto_install=True)
        util.new_module(cr, "hr_work_entry_holidays_enterprise", deps={"hr_work_entry_holidays"}, auto_install=True)
        util.new_module(cr, "l10n_us_1099", deps={"l10n_us", "account_accountant"}, auto_install=True)
        util.force_migration_of_fresh_module(cr, "l10n_us_1099")
        util.new_module(cr, "website_calendar_crm", deps={"website_calendar", "crm"}, auto_install=True)

        util.new_module(cr, "social_youtube", deps={"social", "iap"})
        util.new_module(
            cr,
            "social_test_full",
            deps={
                "social_facebook",
                "social_twitter",
                "social_linkedin",
                "social_push_notifications",
                "social_youtube",
            },
        )
        util.module_deps_diff(cr, "social_demo", plus={"social_youtube"})

        util.module_deps_diff(
            cr, "hr_payroll", plus={"hr_work_entry_contract_enterprise"}, minus={"hr_work_entry_contract"}
        )

        util.module_deps_diff(
            cr,
            "l10n_pe_edi",
            plus={"account_edi"},
            minus={"l10n_latam_invoice_document", "account_debit_note", "account_edi_extended"},
        )

        util.remove_module(cr, "sale_subscription_sepa_direct_debit")
