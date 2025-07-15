from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "l10n_in_upi", "l10n_in")
    util.remove_module(cr, "website_sale_stock_product_configurator")
    if util.has_enterprise():
        util.remove_module(cr, "industry_fsm_forecast")

        # l10n_pe_reports was renamed in 16.1 to l10n_pe_reports_book
        # now we want to merge both
        cr.execute("SELECT 1 FROM ir_module_module WHERE name = 'l10n_pe_reports'")
        if cr.rowcount:
            util.merge_module(cr, "l10n_pe_reports_book", "l10n_pe_reports")
        else:
            # If l10n_pe_reports doesn't exist it means we started the upgrade from 16.0
            # so we need to rename l10n_pe_reports_book back (see base/saas~16.1.1.3/pre-10-modules.py)
            util.rename_module(cr, "l10n_pe_reports_book", "l10n_pe_reports")

    util.merge_module(cr, "l10n_de_skr03", "l10n_de")
    util.merge_module(cr, "l10n_de_skr04", "l10n_de")
    util.merge_module(cr, "mrp_workorder_hr", "mrp_workorder")

    if util.module_installed(cr, "iap_extract") and not util.module_installed(cr, "iap"):
        util.uninstall_module(cr, "iap_extract")
    # https://github.com/odoo/enterprise/pull/52580
    if util.module_installed(cr, "l10n_mx_edi_stock"):
        util.force_upgrade_of_fresh_module(cr, "l10n_mx_edi_stock_30")

    if util.has_enterprise():
        util.force_upgrade_of_fresh_module(cr, "account_online_synchronization")
