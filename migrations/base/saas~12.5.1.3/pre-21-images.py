# -*- coding: utf-8 -*-
import logging

from odoo.tools import image

from odoo.addons.base.maintenance.migrations import util

_logger = logging.getLogger(__name__)


def rename_mixin_fields(cr, model, skip_inherit=()):
    util.update_field_references(cr, "image", "image_1920", only_models=(model,), skip_inherit=skip_inherit)
    util.update_field_references(cr, "image_small", "image_128", only_models=(model,), skip_inherit=skip_inherit)

    util.rename_field(cr, model, "image_original", "image_1920", skip_inherit=skip_inherit)
    util.rename_field(cr, model, "image_big", "image_1024", skip_inherit=skip_inherit)
    util.rename_field(cr, model, "image_large", "image_256", skip_inherit=skip_inherit)
    util.rename_field(cr, model, "image_medium", "image_128", skip_inherit=skip_inherit)
    util.remove_field(cr, model, "can_image_be_zoomed", skip_inherit=skip_inherit)
    util.remove_field(cr, model, "image", skip_inherit=skip_inherit)
    util.remove_field(cr, model, "image_small", skip_inherit=skip_inherit)

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
    tables = set()
    for tbl, _, _, _ in util.get_fk(cr, "ir_attachment"):
        cr.execute(f"SELECT count(*) > %s FROM {tbl}", [util.BIG_TABLE_THRESHOLD // 10])
        if cr.fetchone()[0]:
            tables.add(tbl)
    if tables:
        _logger.info("Reindexing %s tables", len(tables))
        util.parallel_execute(cr, ["REINDEX TABLE {}".format(t) for t in tables])
    new_inherit_mixin(cr, "res.partner")
    new_inherit_mixin(cr, "res.users")  # due to inheritS

    # and the mixin itself
    rename_mixin_fields(cr, "image.mixin", skip_inherit="*")

    # do not recompute on non-concrete models
    util.ENVIRON["s125_image_mixin_recompute"]["512"].remove("image.mixin")

    # Do not limit the size of images already in the database during upgrades.
    image.IMAGE_MAX_RESOLUTION = float("inf")
