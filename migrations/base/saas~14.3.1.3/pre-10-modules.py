# -*- coding: utf-8 -*-
from contextlib import closing

from lxml import etree
from psycopg2.extras import execute_values

from odoo.tools import file_open

from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "account_edi_extended", "account_edi", without_deps=True)

    util.new_module(cr, "gift_card", deps={"sale"})
    util.new_module(cr, "website_sale_gift_card", deps={"website_sale", "gift_card"})

    util.rename_module(cr, "payment_ingenico", "payment_ogone")
    util.rename_module(cr, "payment_odoo_by_adyen", "payment_odoo")

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

        util.remove_module(cr, "sale_subscription_sepa_direct_debit")

    util.remove_record(cr, "base.act_view_currency_rates")
    util.create_column(cr, "res_currency", "full_name", "varchar")
    util.rename_xmlid(cr, "base.SOD", "base.SOS")
    util.rename_xmlid(cr, "base.rateSOD", "base.rateSOS")
    cr.execute("UPDATE res_currency SET name='SOS' WHERE name='SOD'")
    with closing(file_open("addons/base/data/res_currency_data.xml")) as fp:
        tree = etree.parse(fp)
        to_update_values = []
        for node in tree.xpath('//field[@name="full_name"]'):
            to_update_values += [(node.getparent().get("id"), node.text)]
        if to_update_values:
            execute_values(
                cr._obj,
                """
                WITH to_update (name, full_name) AS (VALUES %s)
                UPDATE res_currency
                   SET full_name = to_update.full_name
                  FROM to_update
                 WHERE res_currency.name = to_update.name
            """,
                to_update_values,
            )
