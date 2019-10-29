# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

SUFFIXES = ["big", "large", "medium", "small"]


def image_mixin_recompute_fields(cr, model, infix="", suffixes=SUFFIXES):
    fields = ["image{}_{}".format(infix, s) for s in SUFFIXES]
    fields += ["can_image{}_be_zoomed".format(infix)]
    orig_field = "image{}_original".format(infix)

    ids = util.env(cr)[model].search([(orig_field, "!=", False)]).ids
    util.recompute_fields(cr, model, fields, ids)


def migrate(cr, version):
    # `image_medium` and `image_small` where already there...
    image_mixin_recompute_fields(cr, "product.template", suffixes=SUFFIXES[:2])
    image_mixin_recompute_fields(cr, "product.product", infix="_raw")
