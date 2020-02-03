# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_field(cr, "mrp.bom", "image_small", "image_128")
    util.remove_field(cr, "product.template", "template_attachment_count")
    util.remove_field(cr, "product.product", "product_attachment_count")
