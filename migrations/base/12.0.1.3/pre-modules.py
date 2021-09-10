# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.new_module(cr, "l10n_it_edi", deps={"l10n_it"})  # see odoo/odoo#30845
    util.new_module(cr, "payment_stripe_checkout_webhook", deps={"payment_stripe", "payment_stripe_sca"})
    util.module_deps_diff(cr, "purchase_mrp", plus={"purchase_stock"}, minus={"purchase"})

    # https://github.com/odoo/odoo/pull/38851
    util.new_module(cr, "l10n_dk", deps={"account", "base_iban", "base_vat"})
    # https://github.com/odoo/odoo/pull/32704
    util.new_module(cr, "l10n_id", deps={"account", "base_iban", "base_vat"})
    # https://github.com/odoo/odoo/pull/35566
    util.new_module(cr, "l10n_lt", deps={"l10n_multilang"})
    # https://github.com/odoo/odoo/pull/32830
    util.new_module(cr, "l10n_mn", deps={"account"})
    # https://github.com/odoo/odoo/pull/32468
    util.new_module(cr, "l10n_ua", deps={"account"})
    # https://github.com/odoo/odoo/pull/32685
    util.new_module(cr, "l10n_za", deps={"account", "base_vat"})

    if util.has_enterprise():
        util.module_deps_diff(cr, "stock_account_enterprise", plus={"stock_enterprise"})

        util.new_module(cr, "product_unspsc", deps={"product"})
        util.new_module(
            cr,
            "l10n_co_edi_ubl_2_1",
            deps={"l10n_co_edi", "base_address_city", "product_unspsc"},
        )

        util.new_module(cr, "iot_pairing", deps={"iot"}, auto_install=True)
        util.new_module(cr, "account_ponto", deps={"account_online_sync"}, auto_install=True)

        # https://github.com/odoo/enterprise/pull/10803
        util.new_module(cr, "account_online_synchronization", deps={"account_online_sync"}, auto_install=True)
        # https://github.com/odoo/enterprise/pull/4350
        util.new_module(cr, "l10n_ae_reports", deps={"l10n_ae", "account_reports"}, auto_install=True)
        # https://github.com/odoo/enterprise/pull/3835
        util.new_module(
            cr, "stock_barcode_quality_control", deps={"stock_barcode", "quality_control"}, auto_install=True
        )
        # https://github.com/odoo/enterprise/pull/3517
        util.new_module(cr, "project_enterprise", deps={"project"}, auto_install=True)
        # https://github.com/odoo/enterprise/commit/08efb5d355723639bb4b2489b2c9946aa5eec109
        util.module_deps_diff(cr, "mrp_mps", plus={"purchase_stock"})
        # https://github.com/odoo/enterprise/pull/2806
        util.module_deps_diff(cr, "iot", plus={"mail"})
        # https://github.com/odoo/enterprise/pull/4097
        util.new_module(cr, "l10n_za_reports", deps={"l10n_za", "account_reports"}, auto_install=True)
        # https://github.com/odoo/enterprise/pull/3089, https://github.com/odoo/enterprise/pull/3465
        util.new_module(cr, "sale_intrastat", deps={"sale", "account_intrastat"}, auto_install=True)
        # https://github.com/odoo/enterprise/pull/6167
        util.new_module(cr, "l10n_dk_reports", deps={"l10n_dk", "account_reports"}, auto_install=True)
        # https://github.com/odoo/enterprise/pull/4162
        util.new_module(
            cr, "sale_subscription_taxcloud", deps={"sale_subscription", "account_taxcloud"}, auto_install=True
        )
        # https://github.com/odoo/enterprise/pull/5634
        util.new_module(cr, "l10n_lt_reports", deps={"l10n_lt", "account_reports"}, auto_install=True)
        # https://github.com/odoo/enterprise/pull/4154
        util.new_module(cr, "l10n_mn_reports", deps={"l10n_mn", "account_reports"}, auto_install=True)
        # https://github.com/odoo/enterprise/pull/3812
        util.new_module(cr, "pos_enterprise", deps={"point_of_sale", "web_enterprise"}, auto_install=True)
        # https://github.com/odoo/enterprise/pull/20265 (committed just 4 hours ago...)
        util.new_module(cr, "sale_ebay_account_deletion", deps={"sale_ebay"}, auto_install=True)
