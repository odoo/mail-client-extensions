# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.new_module(cr, "l10n_be_edi", deps={"account", "l10n_be", "account_facturx"}, auto_install=True)
    util.new_module(cr, "sale_product_configurator", deps={"sale"})

    # As sale was split in 2, auto-install module when sale was installed
    if util.modules_installed(cr, ("sale")):
        util.force_install_module(cr, "sale_product_configurator")

    util.new_module(
        cr, "event_sale_product_configurator", deps={"sale_product_configurator", "event_sale"}, auto_install=True
    )

    if not util.has_enterprise():
        util.new_module(cr, "mrp_account", deps={"mrp", "stock_account"}, auto_install=True)
        util.new_module(cr, "sale_coupon", deps={"sale_management"})
        util.new_module(cr, "sale_coupon_delivery", deps={"sale_coupon", "delivery"}, auto_install=True)
        util.new_module(cr, "website_sale_coupon", deps={"website_sale", "sale_coupon"}, auto_install=True)

    util.new_module(
        cr, "website_sale_coupon_delivery", deps={"website_sale_delivery", "sale_coupon_delivery"}, auto_install=True
    )
    util.new_module(
        cr, "website_sale_product_configurator", deps={"website_sale", "sale_product_configurator"}, auto_install=True
    )
    util.new_module(
        cr,
        "website_sale_stock_product_configurator",
        deps={"website_sale_stock", "sale_product_configurator"},
        auto_install=True,
    )

    util.merge_module(cr, "mrp_byproduct", "mrp")

    if util.has_enterprise():
        util.module_deps_diff(cr, "account_asset", plus={"account_reports"}, minus={"account"})
        util.new_module(cr, "helpdesk_sale", deps={"helpdesk", "sale_management"}, auto_install=True)
        util.new_module(cr, "helpdesk_account", deps={"helpdesk_sale", "account"})
        util.new_module(cr, "helpdesk_stock", deps={"helpdesk_sale", "stock"})
        util.new_module(cr, "helpdesk_repair", deps={"helpdesk_stock", "repair"})
        util.new_module(cr, "helpdesk_sale_coupon", deps={"helpdesk_sale", "sale_coupon"})
        util.new_module(cr, "hr_payroll_gantt", deps={"hr_payroll", "web_gantt"}, auto_install=True)
        util.module_deps_diff(cr, "l10n_be_hr_payroll", minus={"l10n_be"})
        util.module_deps_diff(cr, "mail_enterprise", plus={"web_mobile"})
        util.new_module(cr, "mrp_account_enterprise", deps={"mrp_account"}, auto_install=True)
        util.module_deps_diff(cr, "sale_subscription", minus={"account_deferred_revenue"})
        util.module_deps_diff(
            cr, "test_l10n_be_hr_payroll_account", plus={"l10n_generic_coa", "l10n_be", "account_accountant"}
        )

        for cc in "ae ar at au bo br do et gr hr hu jp lu ma no pl ro si th uy vn za".split():
            util.remove_module(cr, "l10n_%s_reports" % cc)

        util.remove_module(cr, "sale_subscription_asset")
        util.merge_module(cr, 'l10n_uk_reports_hmrc', 'l10n_uk_reports')

    else:
        # all payroll modules moved to enterprise
        util.remove_module(cr, "hr_payroll")
        util.remove_module(cr, "hr_payroll_account")
        util.remove_module(cr, "l10n_be_hr_payroll")
        util.remove_module(cr, "l10n_be_hr_payroll_account")
        util.remove_module(cr, "l10n_be_hr_payroll_fleet")
        util.remove_module(cr, "l10n_fr_hr_payroll")
        util.remove_module(cr, "l10n_in_hr_payroll")
