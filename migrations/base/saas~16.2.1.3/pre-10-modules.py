# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_module(cr, "website_payment_paypal")
    util.merge_module(cr, "l10n_generic_coa", "account")
    util.merge_module(cr, "l10n_multilang", "account")
    util.merge_module(cr, "l10n_in_tcs_tds", "l10n_in")
    util.merge_module(cr, "pos_daily_sales_reports", "point_of_sale")
    util.merge_module(cr, "account_sequence", "account")
    util.merge_module(cr, "l10n_latam_account_sequence", "l10n_latam_invoice_document")
    util.merge_module(cr, "website_sale_loyalty_delivery", "website_sale_loyalty")
    util.merge_module(cr, "website_sale_delivery", "website_sale")
    util.merge_module(cr, "website_sale_taxcloud_delivery", "website_sale_account_taxcloud")
    util.rename_module(cr, "website_sale_delivery_mondialrelay", "website_sale_mondialrelay")

    if util.has_enterprise():
        util.remove_module(cr, "l10n_generic_auto_transfer_demo")
        util.remove_module(cr, "event_barcode_mobile")
        util.remove_module(cr, "hr_attendance_mobile")
        util.remove_module(cr, "barcodes_mobile")
        util.remove_module(cr, "project_timesheet_synchro")
        util.remove_module(cr, "test_web_grid")
        util.rename_module(cr, "website_delivery_fedex", "website_sale_fedex")
        util.rename_module(cr, "website_delivery_ups", "website_sale_ups")
        util.remove_module(cr, "sale_subscription_dashboard")
    util.merge_module(cr, "purchase_price_diff", "purchase_stock")
    util.merge_module(cr, "account_payment_invoice_online_payment_patch", "account_payment")
    util.merge_module(cr, "l10n_lu_peppol_id", "account_edi_ubl_cii")

    force_installs = set()
    force_upgrades = {"l10n_mx_edi_sale", "l10n_mx_edi_website_sale"}

    if util.modules_installed(cr, "l10n_be_hr_payroll"):
        force_installs |= {"l10n_be_hr_payroll_sd_worx"}
    if util.modules_installed(cr, "delivery"):
        force_installs |= {"stock_delivery"}
    if util.modules_installed(cr, "delivery") or util.modules_installed(cr, "website_sale", "stock"):
        # `website_sale` now depends on `delivery`. Due to the auto_install flag,
        # `stock_delivery` will be installed. However, we don't want its demo data to be updated.
        cr.execute("SELECT demo FROM ir_module_module WHERE name='stock'")
        if cr.fetchone()[0]:
            # even if there is no upgrade script for this module,
            # we should install it in init=False to avoid updating the noupdate demo data
            force_upgrades |= {"stock_delivery"}

    util.modules_auto_discovery(cr, force_installs=force_installs, force_upgrades=force_upgrades)

    if util.module_installed(cr, "iap_extract") and not util.module_installed(cr, "iap"):
        util.uninstall_module(cr, "iap_extract")
