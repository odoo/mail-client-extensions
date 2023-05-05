# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.modules_auto_discovery(cr)

    util.force_upgrade_of_fresh_module(cr, "website_sale_stock_wishlist")

    util.merge_module(cr, "payment_adyen_paybylink", "payment_adyen")
    # https://github.com/odoo/enterprise/pull/23761
    util.force_upgrade_of_fresh_module(cr, "account_asset_ndt")
