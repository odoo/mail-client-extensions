# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.modules_auto_discovery(cr)

    util.force_upgrade_of_fresh_module(cr, "website_sale_stock_wishlist")
