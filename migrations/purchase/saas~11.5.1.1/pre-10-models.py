# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "purchase_order", "incoterm_id", "int4")
    util.update_field_usage(cr, "purchase.order", "website_url", "access_url")
    util.remove_field(cr, "purchase.order", "website_url")

    util.create_column(cr, "purchase_order_line", "product_uom_qty", "float8")

    # odoo/odoo@5118d248ccf16fe4d2703c2a64e0267f783a56d1
    util.remove_field(cr, "product.template", "purchase_count")
    util.remove_field(cr, "product.product", "purchase_count", drop_column=False)
