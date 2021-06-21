# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.new_module(cr, "l10n_it_edi", deps={"l10n_it"})  # see odoo/odoo#30845
    util.new_module(cr, "payment_stripe_checkout_webhook", deps={"payment_stripe", "payment_stripe_sca"})
    util.module_deps_diff(cr, "purchase_mrp", plus={"purchase_stock"}, minus={"purchase"})

    if util.has_enterprise():
        util.new_module(cr, "l10n_uk_reports_hmrc", deps={"l10n_uk_reports"}, auto_install=True)
        util.module_deps_diff(cr, "stock_account_enterprise", plus={"stock_enterprise"})

        # https://github.com/odoo/enterprise/pull/6357
        util.new_module(cr, "account_reports_cash_flow", deps={"account_reports"}, auto_install=True)

        util.new_module(cr, "product_unspsc", deps={"product"})
        util.new_module(
            cr,
            "l10n_co_edi_ubl_2_1",
            deps={"l10n_co_edi", "base_address_city", "product_unspsc"},
        )

        util.new_module(cr, "iot_pairing", deps={"iot"}, auto_install=True)
        util.new_module(cr, "account_ponto", deps={"account_online_sync"}, auto_install=True)
