# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_sale.header")
    util.rename_xmlid(cr, "website_sale.hide_cart_if_empty", "website_sale.header_hide_empty_cart_link")
    util.remove_record(cr, "website_sale.action_abandoned_orders_ecommerce")
