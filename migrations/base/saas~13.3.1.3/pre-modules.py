# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.new_module(cr, "mrp_landed_costs", deps={"stock_landed_costs", "mrp"}, auto_install=True)
    util.module_deps_diff(cr, "sale_coupon", plus={"sale"}, minus={"sale_management"})
