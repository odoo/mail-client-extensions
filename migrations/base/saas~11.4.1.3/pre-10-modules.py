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

    if util.has_enterprise():
        util.new_module(cr, "delivery_easypost", deps={"delivery", "mail"})
        util.new_module(cr, "web_cohort", deps={"web"}, auto_install=True)

        util.module_deps_diff(cr, "inter_company_rules", plus={"purchase_stock"}, minus={"purchase"})
        util.module_deps_diff(cr, "mrp_workorder", plus={"barcodes"})
        util.module_deps_diff(cr, "quality_mrp_workorder", plus={"barcodes"})
        util.module_deps_diff(cr, "sale_subscription", plus={"web_cohort"})
        util.module_deps_diff(cr, "stock_barcode", plus={"web_tour"})

    util.remove_module(cr, "auth_crypt")
