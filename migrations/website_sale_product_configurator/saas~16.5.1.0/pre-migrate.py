# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_sale_product_configurator.product_quantity_config_website")
    util.remove_view(cr, "website_sale_product_configurator.configure_optional_products_website")
    util.remove_view(cr, "website_sale_product_configurator.configure")
