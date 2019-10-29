# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    env = util.env(cr)
    suffixes = ["big", "large", "medium", "small"]

    # `image_medium` and `image_small` where already there...
    fields = ["image_{}".format(s) for s in suffixes[:2]] + ["can_image_be_zoomed"]
    ids = env["product.template"].search([("image_original", "!=", False)]).ids
    util.recompute_fields(cr, "product.template", fields, ids)

    fields = ["image_raw_{}".format(s) for s in suffixes] + ["can_image_raw_be_zoomed"]
    ids = env["product.product"].search([("image_raw_original", "!=", False)]).ids
    util.recompute_fields(cr, "product.product", fields, ids)
