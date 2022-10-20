# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # renames
    util.rename_module(cr, "crm_iap_lead_enrich", "crm_iap_enrich")
    util.rename_module(cr, "crm_iap_lead", "crm_iap_mine")
    util.rename_module(cr, "crm_iap_lead_website", "website_crm_iap_reveal")

    # OCA module wildly used
    cr.execute(
        """
        SELECT 1
          FROM ir_module_module
         WHERE name = 'l10n_eu_oss'
           AND author ILIKE '%Odoo Community Association (OCA)%'
        """
    )
    if cr.rowcount:
        util.rename_module(cr, "l10n_eu_oss", "l10n_eu_oss_oca")  # nofml
    util.rename_module(cr, "l10n_eu_service", "l10n_eu_oss")

    # merges
    util.merge_module(cr, "website_form", "website")
    util.merge_module(cr, "website_animate", "website", update_dependers=False)

    if util.has_enterprise():
        # renames
        util.rename_module(cr, "crm_enterprise_iap_lead_website", "website_crm_iap_reveal_enterprise")
        util.rename_module(cr, "website_calendar", "appointment")
        util.rename_module(cr, "website_calendar_crm", "appointment_crm")

        # merges
        util.merge_module(cr, "l10n_lu_reports_electronic", "l10n_lu_reports")
        util.merge_module(cr, "l10n_lu_reports_electronic_xml_2_0", "l10n_lu_reports")
        util.merge_module(cr, "l10n_lu_saft", "l10n_lu_reports")
        util.merge_module(cr, "sale_amazon_delivery", "sale_amazon")
        util.merge_module(cr, "sale_ebay_account_deletion", "sale_ebay")

    force_installs = None
    if util.table_exists(cr, "mail_channel"):
        # Install the new mail_group module if there's some "mail_channel" with "email_send=True" in the database
        cr.execute("SELECT 1 FROM mail_channel WHERE email_send=TRUE FETCH FIRST ROW ONLY")
        if cr.rowcount:
            force_installs = {"mail_group"}

    util.modules_auto_discovery(cr, force_installs=force_installs)

    util.force_upgrade_of_fresh_module(cr, "mail_group")
    util.force_upgrade_of_fresh_module(cr, "sale_gift_card")
    util.force_upgrade_of_fresh_module(cr, "sale_planning")
    util.force_upgrade_of_fresh_module(cr, "sale_project_forecast")
    util.force_upgrade_of_fresh_module(cr, "sale_timesheet_margin")

    if util.has_enterprise():
        # removals
        util.remove_module(cr, "mail_github")
        util.remove_module(cr, "stock_barcode_mobile")

    # removals
    util.remove_module(cr, "adyen_platforms")
    util.remove_module(cr, "payment_odoo")
    util.remove_module(cr, "sale_payment_odoo")
    util.remove_module(cr, "sale_timesheet_purchase")
    util.remove_module(cr, "website_mail_channel")
    util.remove_module(cr, "website_sale_blog")
    util.remove_module(cr, "website_sale_management")

    # cleaning
    cr.execute("DROP TABLE IF EXISTS product_blogpost_rel")
