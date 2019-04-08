# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "purchase_order", "incoterm_id", "int4")
    util.update_field_references(cr, "website_url", "access_url", only_models=["purchase.order"])
    util.remove_field(cr, "purchase.order", "website_url")

    util.create_column(cr, "purchase_order_line", "product_uom_qty", "float8")
