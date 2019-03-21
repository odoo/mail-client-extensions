# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def image_mixin_recompute_fields(cr, model, image_field_fix=""):
    fields = [f % image_field_fix for f in ["image%s_big", "image%s_large", "image%s_medium", "image%s_small", "can_image%s_be_zoomed"]]
    ids = util.env(cr)[model].search([("image%s_original" % image_field_fix, "!=", False)]).ids
    util.recompute_fields(cr, model, fields, ids)


def migrate(cr, version):
    image_mixin_recompute_fields(cr, "product.template")
    image_mixin_recompute_fields(cr, "product.product", "_raw")
