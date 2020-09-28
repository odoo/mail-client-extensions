# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.new_module(cr, "adyen_platforms", deps={"mail", "web"})
    util.new_module(cr, "payment_odoo_by_adyen", deps={"payment", "adyen_platforms"})
    util.module_deps_diff(cr, "pos_adyen", plus={"adyen_platforms"})
