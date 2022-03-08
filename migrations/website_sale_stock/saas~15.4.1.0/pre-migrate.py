# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_sale_stock.website_sale_stock_payment")
    util.remove_field(cr, "product.product", "cart_qty")
