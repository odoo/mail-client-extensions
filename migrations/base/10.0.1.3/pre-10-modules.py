# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.new_module(cr, "l10n_be_intrastat_2019", deps=("l10n_be_intrastat",), auto_install=True)
    util.new_module(cr, "payment_stripe_sca", deps={"payment_stripe"}, auto_install=True)
    util.new_module(cr, "hr_expense_check", deps={"hr_expense", "account_check_printing"}, auto_install=True)
    util.new_module(cr, "account_lock", deps={"account"})  # also in 9.0, but not in the intermediate saas versions

    util.module_deps_diff(cr, "l10n_mx", plus={"account_tax_cash_basis"})

    if util.has_enterprise():
        util.new_module(cr, "web_mobile", deps=("web_settings_dashboard",), auto_install=True)
        util.new_module(cr, "mail_push", deps=("mail", "web_mobile"), auto_install=True)
        util.new_module(cr, "sale_account_taxcloud", deps={"account_taxcloud", "sale"}, auto_install=True)
        util.new_module(cr, "stock_barcode_mobile", deps=("stock_barcode", "web_mobile"), auto_install=True)
        util.new_module(cr, "hr_expense_sepa", deps=("account_sepa", "hr_expense"), auto_install=True)
        util.new_module(
            cr, "website_sale_account_taxcloud", deps={"account_taxcloud", "website_sale"}, auto_install=True
        )
        util.new_module(
            cr,
            "website_sale_taxcloud_delivery",
            deps=("website_sale_delivery", "website_sale_account_taxcloud"),
            auto_install=True,
        )
        util.new_module(cr, "l10n_uk_reports_hmrc", deps={"l10n_uk_reports"}, auto_install=True)

        util.new_module_dep(cr, "web_studio", "portal")

    # modules added after release
    util.new_module(cr, "hw_screen", deps={"hw_proxy"})
    util.new_module(cr, "account_cash_basis_base_account", deps={"account_tax_cash_basis"}, auto_install=True)
    util.new_module(cr, "l10n_in_schedule6", deps={"account"})

    util.new_module(cr, "l10n_fr_certification", deps={"l10n_fr"})
    util.new_module(cr, "l10n_fr_sale_closing", deps={"l10n_fr_certification"}, auto_install=True)
    util.new_module(cr, "l10n_fr_pos_cert", deps={"l10n_fr_sale_closing", "point_of_sale"})
    # The module has also been added in saas~11
    util.module_deps_diff(cr, "l10n_fr_pos_cert", plus={"l10n_fr_sale_closing"}, minus={"l10n_fr_certification"})
