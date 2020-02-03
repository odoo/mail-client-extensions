# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def rename_mixin_fields(cr, model):
    util.update_field_references(cr, "image", "image_1920", only_models=(model,))
    util.update_field_references(cr, "image_small", "image_128", only_models=(model,))

    util.rename_field(cr, model, "image_original", "image_1920")
    util.rename_field(cr, model, "image_big", "image_1024")
    util.rename_field(cr, model, "image_large", "image_256")
    util.rename_field(cr, model, "image_medium", "image_128")
    util.remove_field(cr, model, "can_image_be_zoomed")
    util.remove_field(cr, model, "image")
    util.remove_field(cr, model, "image_small")

    util.ENVIRON["s125_image_mixin_recompute"]["512"].append(model)


def new_inherit_mixin(cr, model):
    util.update_field_references(cr, "image_small", "image_128", only_models=(model,))

    util.rename_field(cr, model, "image", "image_1920")
    util.rename_field(cr, model, "image_medium", "image_128")
    util.remove_field(cr, model, "image_small")

    util.ENVIRON["s125_image_mixin_recompute"]["all"].append(model)


def single_image(cr, model):
    # special case, only an `image_128 field`
    util.update_field_references(cr, "image", "image_128", only_models=(model,))
    util.update_field_references(cr, "image_small", "image_128", only_models=(model,))

    util.rename_field(cr, model, "image_medium", "image_128")
    util.remove_field(cr, model, "image")
    util.remove_field(cr, model, "image_small")


def migrate(cr, version):
    util.ENVIRON["s125_image_mixin_recompute"] = {"all": [], "512": []}
    new_inherit_mixin(cr, "res.partner")
