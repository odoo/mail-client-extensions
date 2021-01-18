# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "product_product", "service_upsell_warning", "boolean", default=False)
    util.create_column(cr, "product_product", "service_upsell_threshold", "float8")
    util.create_column(cr, "sale_order_line", "has_displayed_warning_upsell", "boolean", default=False)
