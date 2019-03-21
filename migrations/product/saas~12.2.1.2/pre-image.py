# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_field(cr, "product.template", "image", "image_raw_original", update_references=False)
    util.rename_field(cr, "product.template", "image_medium", "image_raw_medium", update_references=False)
    util.rename_field(cr, "product.template", "image_small", "image_raw_small", update_references=False)
    util.create_column(cr, "product_template", "can_image_raw_be_zoomed", "boolean")

    util.rename_field(cr, "product.product", "image_variant", "image_raw_original")
    util.rename_field(cr, "product.product", "image", "image_big")
    util.create_column(cr, "product_product", "can_image_raw_be_zoomed", "boolean")
