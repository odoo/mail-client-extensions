# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.new_module(cr, "iap", deps={"web"}, auto_install=True)
    util.new_module(cr, "pos_cash_rounding", deps={"point_of_sale"}, auto_install=True)

    if not util.has_enterprise():
        # moved from enterprise \o/
        util.new_module(cr, "sms", deps={"iap", "mail"}, auto_install=True)
        util.new_module(cr, "calendar_sms", deps={"calendar", "sms"}, auto_install=True)
    else:
        util.new_module_dep(cr, "account_accountant", "account_reports")
        util.new_module_dep(cr, "sms", "iap")
        util.remove_module(cr, "sms_fortytwo")

        util.new_module(cr, "barcodes_mobile", deps={"barcodes", "web_mobile"}, auto_install=True)
        util.new_module(cr, "sale_coupon_taxcloud", deps={"sale_account_taxcloud", "sale_coupon"}, auto_install=True)
        util.new_module(
            cr,
            "sale_coupon_taxcloud_delivery",
            deps={"sale_coupon_taxcloud", "sale_coupon_delivery"},
            auto_install=True,
        )

        if "saas" in version:
            # for saas-{14,15} databases
            util.new_module(cr, "payment_stripe_sca", deps={"payment_stripe"}, auto_install=True)

        # This module is present in saas-14. This module is not installable nor usable as the certificate in the code is expired.
        # There is no database that should have this module installed.
        util.merge_module(cr, "l10n_mx_edi_cfdi_33", "l10n_mx_edi")

        util.new_module(cr, "l10n_mx_edi_cancellation", deps={"l10n_mx_edi"}, auto_install=True)
        util.new_module(cr, "l10n_mx_edi_customs", deps={"l10n_mx_edi"})
        util.new_module(cr, "l10n_mx_edi_external_trade", deps={"l10n_mx_edi"})
        util.new_module(cr, "l10n_mx_edi_payment_bank", deps={"l10n_mx_edi"}, auto_install=True)
        util.new_module(cr, "l10n_mx_tax_cash_basis", deps={"l10n_mx_edi"}, auto_install=True)
        util.new_module(
            cr,
            "l10n_mx_edi_landing",
            deps={"stock_landed_costs", "sale_management", "account_accountant", "l10n_mx_edi_customs"},
        )
        util.new_module(cr, "l10n_mx_edi_sale_coupon", deps={"l10n_mx_edi", "sale_coupon"}, auto_install=True)
        util.new_module(cr, "l10n_mx_reports_closing", deps={"l10n_mx_reports"}, auto_install=True)

        # https://github.com/odoo/enterprise/pull/6291
        util.new_module(cr, "account_reports_cash_flow", deps={"account_reports"}, auto_install=True)

        util.module_deps_diff(cr, "pos_blackbox_be", plus={"l10n_be", "web_enterprise"}, minus={"web", "point_of_sale"})

    # Somehow, this is possible to have the default or bootswatch theme installed in addition to one other theme
    # if you come from Odoo 9.0 or Odoo 10.0, but Odoo 11.0 doesn't support it.
    if util.module_installed(cr, "website"):
        cr.execute(
            """
                SELECT name
                FROM ir_module_module
                WHERE name like 'theme_%%'
                AND state in %s
            """,
            (util.INSTALLED_MODULE_STATES,),
        )
        installed_themes = [t[0] for t in cr.fetchall()]
        for theme in ["theme_default", "theme_bootswatch"]:
            if len(installed_themes) > 1 and theme in installed_themes:
                util.uninstall_module(cr, theme)
                installed_themes.remove(theme)
