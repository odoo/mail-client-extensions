# -*- coding: utf-8 -*-
import os

import psycopg2

from odoo.tools.misc import str2bool

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_module(cr, "crm_project")  # artefact that may stay in old databases
    util.rename_module(cr, "crm_project_issue", "crm_project")
    util.rename_module(cr, "website_issue", "website_form_project")
    util.rename_module(cr, "website_portal", "portal")
    util.rename_module(cr, "website_rating_project_issue", "website_rating_project")

    util.new_module(cr, "account_payment", deps={"account", "payment"})
    util.new_module(cr, "http_routing", deps={"web"})
    util.new_module(cr, "transifex", deps={"base"})

    util.module_deps_diff(cr, "portal", plus={"http_routing", "mail"}, minus={"website", "auth_signup"})
    util.new_module_dep(cr, "account", "portal")

    # Avoid to have account depending on website...
    # Then let oneAppFree remains oneAppFree
    util.merge_module(cr, "website_account", "account", without_deps=True)

    accountant_deps = util.splitlines(
        """
        account_asset
        account_bank_statement_import
        hr_expense
        l10n_be_intrastat
        l10n_eu_service
        l10n_fr_fec
        # test_main_flows

        # enterprise modules
        account_reports_followup
    """
    )
    for m in accountant_deps:
        util.module_deps_diff(cr, m, plus={"account"}, minus={"account_accountant"})

    util.new_module_dep(cr, "delivery", "sale_management")

    # l10n_in
    util.module_deps_diff(cr, "l10n_in", plus={"account_tax_python"}, minus={"account"})
    util.module_deps_diff(cr, "l10n_in_schedule6", plus={"account_tax_python"}, minus={"account"})
    util.new_module(cr, "l10n_in_purchase", deps={"l10n_in", "purchase"}, auto_install=True)
    util.new_module(cr, "l10n_in_sale", deps={"l10n_in", "sale"}, auto_install=True)
    util.new_module(cr, "l10n_in_stock", deps={"l10n_in", "stock"}, auto_install=True)

    util.new_module_dep(cr, "l10n_nl", "base_address_extended")

    # Avoid to install stock module just because procurement was auto-installed...
    # Then let oneAppFree remains oneAppFree
    util.module_deps_diff(cr, "sale", minus={"procurement"})
    if util.module_installed(cr, "procurement"):
        if str2bool(os.environ.get("ODOO_MIG_FORCE_PROCUREMENT_UNINSTALL_11", "0")):
            util.uninstall_module(cr, "procurement")
        else:
            # determine if really used
            cr.execute(
                """
                SELECT COUNT(*)
                FROM ir_module_module_dependency d
            INNER JOIN ir_module_module m ON d.module_id = m.id
                WHERE d.name = 'procurement'
                AND m.state IN %s
            """,
                [util._INSTALLED_MODULE_STATES],
            )
            if not cr.fetchone()[0]:
                cr.execute("SELECT COUNT(1) FROM procurement_order")
                if not cr.fetchone()[0]:
                    util.uninstall_module(cr, "procurement")

    sale_stock_installed = util.module_installed(cr, "sale_stock")
    util.merge_module(cr, "procurement", "stock")
    if (
        util.parse_version(version) < util.parse_version("10.saas~14")
        and util.module_installed(cr, "sale_stock") != sale_stock_installed
    ):
        # for databases < saas~14, if sale_stock is going to be auto installed via module merge,
        # we need to manually rename xmlid to avoid duplicated group. See #369
        util.import_script("sale_stock/10.saas~14.1.0/pre-renames.py").migrate(cr, version)

    util.new_module_dep(cr, "project", "portal")
    util.merge_module(cr, "project_issue", "project")  # will handle deps

    util.new_module_dep(cr, "sale", "portal")
    util.module_deps_diff(cr, "sale_crm", plus={"sale_management"}, minus={"sale"})
    # Do not undo what have been done in saas~17 as it has to be redo in 11.0
    # saas~18 being a dead release (no one use it), we can keep currently correct dependencies
    # util.module_deps_diff(cr, 'sale_stock', plus={'sale'}, minus={'sale_management'})

    util.module_deps_diff(cr, "website", plus={"http_routing", "portal"})

    util.module_deps_diff(cr, "website_quote", minus={"website_portal_sale"})
    util.module_deps_diff(
        cr, "website_rating_project", plus={"website", "rating_project"}, minus={"website_project_issue"}
    )
    util.module_deps_diff(cr, "website_sale", minus={"website_portal_sale", "website_account"})
    util.module_deps_diff(cr, "website_sale_digital", plus={"website_sale"}, minus={"website_portal_sale"})

    util.merge_module(cr, "website_portal_purchase", "purchase")
    util.merge_module(cr, "website_portal_sale", "sale")

    util.remove_view(cr, "website_project.my_projects")
    util.merge_module(cr, "website_project", "project")
    util.merge_module(cr, "website_project_issue", "project")

    util.new_module(
        cr, "website_sale_stock_options", deps={"website_sale_stock", "website_sale_options"}, auto_install=True
    )

    if util.has_enterprise():
        has_workitems = False
        if util.table_exists(cr, "marketing_campaign_workitem"):
            cr.execute("SELECT COUNT(*) FROM marketing_campaign_workitem")
            has_workitems = cr.fetchone()[0] > 0
        if has_workitems:
            util.rename_module(cr, "marketing_campaign", "marketing_automation")
            util.module_deps_diff(
                cr, "marketing_automation", plus={"mass_mailing"}, minus={"document", "mail", "decimal_precision"}
            )
        else:
            util.new_module(
                cr,
                "marketing_automation",
                deps={"mass_mailing"},
                auto_install=util.module_installed(cr, "marketing_campaign"),
            )
            util.remove_module(cr, "marketing_campaign")

        util.merge_module(cr, "crm_voip", "voip")
        util.merge_module(cr, "website_subscription", "sale_subscription")
        util.new_module(cr, "account_sepa_direct_debit", deps={"account", "base_iban"})
        util.new_module(cr, "helpdesk_timesheet", deps={"helpdesk", "hr_timesheet"})
        util.new_module(cr, "helpdesk_sale_timesheet", deps={"helpdesk_timesheet", "sale_timesheet"}, auto_install=True)
        try:
            with util.savepoint(cr):
                util.new_module(cr, "event_barcode_mobile", deps={"event_barcode", "web_mobile"}, auto_install=True)
        except psycopg2.Error:
            pass

        util.new_module(cr, "l10n_de_reports", deps={"l10n_de", "account_reports"}, auto_install=True)

        util.module_deps_diff(cr, "helpdesk", plus={"resource", "portal"})
        util.module_deps_diff(
            cr,
            "l10n_mx_edi",
            plus={"account_invoicing", "account_cancel", "document", "base_address_city"},
            minus={"account"},
        )
        util.module_deps_diff(cr, "mrp_maintenance", plus={"quality_mrp"}, minus={"mrp_workorder"})
        util.new_module_dep(cr, "mrp_mps", "purchase")
        util.module_deps_diff(cr, "sale_subscription", plus={"portal", "sale_payment"})

        util.module_deps_diff(cr, "voip", plus={"mail", "phone_validation"}, minus={"sales_team"})
        util.new_module(cr, "voip_onsip", deps={"voip"})
        util.new_module_dep(cr, "web_studio", "web_enterprise")
        util.module_deps_diff(cr, "website_helpdesk", plus={"website"}, minus={"portal", "website_form_editor"})
        util.new_module_dep(cr, "website_helpdesk_form", "website_form_editor")
        util.new_module_dep(cr, "website_sign", "portal")
        if util.table_exists(cr, "project_issue") and os.environ.get("ODOO_MIG_S18_HELPDESK_ISSUES"):
            util.force_install_module(cr, "helpdesk")
    else:
        # you're screw...
        util.remove_module(cr, "marketing_campaign")
        util.remove_module(cr, "account_accountant")

    util.rename_xmlid(cr, *util.expand_braces("rating_project{,_issue}.mt_issue_rating"))
    util.rename_xmlid(cr, *util.expand_braces("rating_project{,_issue}.mt_project_issue_rating"))
    util.move_field_to_module(cr, "account.analytic.line", "issue_id", "project_issue_sheet", "project")

    removed_modules = util.splitlines(
        """
        marketing_campaign_crm_demo

        project_issue_sheet
        website_project_issue_sheet
        rating_project_issue

        stock_calendar  # merge somewhere?
        website_project_timesheet

        # enterprise modules
        l10n_de_skr03_reports
        l10n_de_skr04_reports
        mrp_barcode
    """
    )

    for m in removed_modules:
        util.remove_module(cr, m)
