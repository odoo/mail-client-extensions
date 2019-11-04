# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_field(cr, "product.template", "image", "image_original", update_references=False)
    if util.table_exists(cr, "product_template"):
        util.create_column(cr, "product_template", "can_image_raw_be_zoomed", "boolean")

    util.rename_field(cr, "product.product", "image_variant", "image_raw_original")
    util.rename_field(cr, "product.product", "image", "image_big", update_references=False)
    if util.table_exists(cr, "product_product"):
        util.create_column(cr, "product_product", "can_image_raw_be_zoomed", "boolean")
