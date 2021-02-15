# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, 'website_sale_coupon.cart_popover')
    util.remove_view(cr, 'website_sale_coupon.website_sale_coupon_cart_summary_show_img')
