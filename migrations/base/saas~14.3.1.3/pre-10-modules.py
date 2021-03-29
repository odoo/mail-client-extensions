# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "account_edi_extended", "account_edi", without_deps=True)

    util.new_module(cr, "gift_card", deps={"sale"})
    util.new_module(cr, "website_sale_gift_card", deps={"website_sale", "gift_card"})

    util.module_deps_diff(cr, "l10n_pe", plus={"l10n_latam_invoice_document", "account_debit_note"})

    util.remove_module_deps(cr, "website_hr_recruitment", {"website_partner"})
    util.module_auto_install(cr, "website_hr_recruitment", ["hr_recruitment", "website_mail"])

    util.module_deps_diff(cr, "mail_client_extension", minus={"crm", "crm_iap_lead_enrich"}, plus={"contacts", "iap"})
    util.rename_module(cr, "mail_client_extension", "mail_plugin")

    util.new_module(cr, "crm_mail_plugin", deps={"crm", "mail_plugin"}, auto_install=True)

    if util.has_enterprise():
        util.merge_module(cr, "l10n_be_hr_payroll_273S_274", "l10n_be_hr_payroll")
        util.merge_module(cr, "l10n_be_hr_payroll_273S_274_account", "l10n_be_hr_payroll_account")
        util.merge_module(cr, "documents_l10n_be_hr_payroll_273S_274", "documents_l10n_be_hr_payroll")
        util.merge_module(cr, "l10n_be_hr_payroll_impulsion", "l10n_be_hr_payroll")

        util.module_deps_diff(
            cr,
            "l10n_pe_edi",
            plus={"account_edi"},
            minus={"l10n_latam_invoice_document", "account_debit_note", "account_edi_extended"},
        )

        util.merge_module(cr, "l10n_be_hr_payroll_onss_restructuring", "l10n_be_hr_payroll")

        util.new_module(cr, "hr_work_entry_contract_enterprise", deps={"hr_work_entry_contract"}, auto_install=True)
        util.new_module(cr, "hr_work_entry_holidays_enterprise", deps={"hr_work_entry_holidays"}, auto_install=True)
        util.module_deps_diff(
            cr, "hr_payroll", plus={"hr_work_entry_contract_enterprise"}, minus={"hr_work_entry_contract"}
        )

        util.new_module(cr, "website_calendar_crm", deps={"website_calendar", "crm"}, auto_install=True)

        util.new_module(cr, "helpdesk_mail_plugin", deps={"helpdesk", "mail_plugin"}, auto_install=True)
