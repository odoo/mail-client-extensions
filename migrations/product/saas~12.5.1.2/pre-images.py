# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.update_field_usage(cr, "product.product", "image_raw_small", "image_variant_128")
    util.rename_field(cr, "product.product", "image_raw_original", "image_variant_1920")
    util.rename_field(cr, "product.product", "image_raw_big", "image_variant_1024")
    util.rename_field(cr, "product.product", "image_raw_large", "image_variant_256")
    util.rename_field(cr, "product.product", "image_raw_medium", "image_variant_128")
    util.remove_field(cr, "product.product", "image_raw_small")
    util.rename_field(cr, "product.product", "can_image_raw_be_zoomed", "can_image_variant_1024_be_zoomed")
    util.rename_field(cr, "product.product", "can_image_be_zoomed", "can_image_1024_be_zoomed")
    util.rename_field(cr, "product.template", "can_image_be_zoomed", "can_image_1024_be_zoomed")

    imp = util.import_script("base/saas~12.5.1.3/pre-21-images.py")
    imp.rename_mixin_fields(cr, "product.template")
    imp.rename_mixin_fields(cr, "product.product")
