# -*- coding: utf-8 -*-
from odoo import tools

from odoo.upgrade import util


def migrate(cr, version):
    tools.config["default_productivity_apps"] = False  # don't auto-install productivity apps on upgrade

    util.force_migration_of_fresh_module(cr, "account_edi_ubl_cii")

    util.rename_xmlid(cr, "l10n_be_edi.edi_efff_1", "account_edi_ubl_cii.edi_efff_1")
    util.rename_xmlid(cr, "l10n_nl_edi.edi_nlcius_1", "account_edi_ubl_cii.edi_nlcius_1")
    util.rename_xmlid(cr, "l10n_no_edi.edi_ehf_3", "account_edi_ubl_cii.edi_ehf_3")

    util.remove_module(cr, "l10n_be_edi")
    util.remove_module(cr, "l10n_nl_edi")
    util.remove_module(cr, "l10n_no_edi")

    util.merge_module(cr, "account_edi_ubl", "account_edi_ubl_cii")
    util.merge_module(cr, "account_edi_ubl_bis3", "account_edi_ubl_cii")
    util.merge_module(cr, "account_edi_facturx", "account_edi_ubl_cii")
    util.merge_module(cr, "l10n_it_edi_sdicoop", "l10n_it_edi")

    util.merge_module(cr, "fetchmail", "mail")
    util.merge_module(cr, "fetchmail_gmail", "google_gmail")
    util.merge_module(cr, "fetchmail_outlook", "microsoft_outlook")

    util.remove_module(cr, "purchase_requisition_stock_dropshipping")

    if util.module_installed(cr, "google_spreadsheet"):
        util.add_to_migration_reports(
            """
                <p><strong>Important notice regarding Google Spreadsheet</strong></p>
                <p>
                    The Google Spreadsheet integration has been removed from Odoo 16.0.
                </p>
                <p>
                    Spreadsheets created before the upgrade will keep working,
                    provided that the data they fetch is still in the same format as
                    in your previous version, but you will not be able to create new
                    spreadsheets after the upgrade.
                </p>
                <p>
                    We advise you to use the Documents application and the
                    Odoo-integrated spreadsheets to replace that feature.
                </p>
            """,
            category="Removed modules",
            format="html",
        )

    util.remove_module(cr, "google_drive")
    util.remove_module(cr, "google_spreadsheet")

    util.remove_module(cr, "website_utm")

    util.remove_module(cr, "transifex")

    if util.has_enterprise():
        util.force_migration_of_fresh_module(cr, "spreadsheet_edition")
        util.remove_module(cr, "project_account_accountant")
        util.remove_module(cr, "sale_project_enterprise")
        util.merge_module(cr, "account_intrastat_expiry", "account_intrastat")
        util.merge_module(cr, "l10n_mx_xml_polizas_edi", "l10n_mx_xml_polizas")

    util.remove_module(cr, "l10n_nl_report_intrastat")
    util.remove_module(cr, "l10n_es_reports_2021")
    util.remove_module(cr, "l10n_mx_reports_closing")

    util.rename_module(cr, "payment_test", "payment_demo")
    util.rename_module(cr, "payment_transfer", "payment_custom")

    if util.module_installed(cr, "payment"):
        util.force_install_module(cr, "account_payment")

    util.force_upgrade_of_fresh_module(cr, "hr_hourly_cost")
    util.force_upgrade_of_fresh_module(cr, "hr_recruitment_skills")
    util.remove_module(cr, "planning_calendar")

    if util.has_enterprise():
        util.remove_module(cr, "fleet_dashboard")
        util.remove_module(cr, "im_livechat_enterprise")
        util.remove_module(cr, "purchase_stock_enterprise")
        util.remove_module(cr, "website_slides_enterprise")
        util.remove_module(cr, "web_dashboard")
