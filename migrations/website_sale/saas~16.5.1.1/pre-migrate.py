# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "module_website_sale_digital")
    util.remove_view(cr, "website_sale.cart_popover")
    util.remove_view(cr, "website_sale.cart_summary")
    util.remove_view(cr, "website_sale.extra_info_option")
    util.remove_view(cr, "website_sale.payment_sale_note")
    util.remove_view(cr, "website_sale.payment_footer")
    util.remove_view(cr, "website_sale.short_cart_summary")
