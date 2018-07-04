# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.new_module(cr, "purchase_stock", deps={"stock_account", "purchase"}, auto_install=True)

    util.module_deps_diff(cr, "account_payment", minus={"account"})

    util.module_deps_diff(cr, "purchase", plus={"account"}, minus={"stock_account"})
    util.module_deps_diff(cr, "purchase_requisition", plus={"purchase_stock"}, minus={"purchase"})
    util.module_deps_diff(cr, "stock_dropshipping", plus={"purchase_stock"}, minus={"purchase"})
    util.module_deps_diff(cr, "stock_landed_costs", plus={"purchase_stock"}, minus={"purchase"})
    util.module_deps_diff(cr, "test_main_flows", plus={"purchase_stock"}, minus={"purchase"})

    util.module_deps_diff(cr, "website_quote", minus={"payment"})

    util.remove_module(cr, "auth_crypt")
