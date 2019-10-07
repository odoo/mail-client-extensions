# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.module_installed(cr, "product") and util.parse_version(version) < util.parse_version("saas~12.2"):
        util.import_script("product/saas~12.2.1.2/pre-image.py").migrate(cr, version)

    # product.product variant fields
    util.rename_field(cr, "product.product", "image_raw_original", "image_variant_1920")
    util.renmae_field(cr, "product.product", "image_raw_big", "image_variant_1024")
    util.renmae_field(cr, "product.product", "image_raw_large", "image_variant_256")
    util.renmae_field(cr, "product.product", "image_raw_medium", "image_variant_128")
    util.update_field_references(cr, "image_raw_small", "image_variant_128", only_models=("product.product",))
    util.remove_field(cr, "product.product", "image_raw_small")
    util.rename_field(cr, "product.product", "can_image_raw_be_zoomed", "can_image_variant_1024_be_zoomed")
    util.rename_field(cr, "product.product", "can_image_be_zoomed", "can_image_1024_be_zoomed")
    util.rename_field(cr, "product.template", "can_image_be_zoomed", "can_image_1024_be_zoomed")
    util.rename_field(cr, "product.image", "can_image_be_zoomed", "can_image_1024_be_zoomed")

    models = util.splitlines(
        """
        product.product
        product.template
        forum.forum
        product.image
        slide.channel
        slide.slide
    """
    )

    util.update_field_references(cr, "image", "image_1920", only_models=tuple(models))
    util.update_field_references(cr, "image_small", "image_128", only_models=tuple(models))

    for model in models:
        util.rename_field(cr, model, "image_original", "image_1920")
        util.rename_field(cr, model, "image_big", "image_1024")
        util.rename_field(cr, model, "image_large", "image_256")
        util.rename_field(cr, model, "image_medium", "image_128")
        util.remove_field(cr, model, "can_image_be_zoomed")
        util.remove_field(cr, model, "image")
        util.remove_field(cr, model, "image_small")

    # models that wasn't inheriting from `image.mixin` before but had some image fields
    new_models = util.splitlines("""
        res.partner
        lunch.product
        gamification.badge
        gamification.karma.rank
        hr.employee
        hr.employee.public
        product.public.category
    """)
    util.update_field_references(cr, "image_small", "image_128", only_models=tuple(new_models))
    for model in new_models:
        util.rename_field(cr, model, "image", "image_1920")
        util.rename_field(cr, model, "image_medium", "image_128")
        util.remove_field(cr, model, "image_small")

    # Other special cases, only a `image_128 field`
    other_models = util.splitlines("""
        mail.channel
        im_livechat.channel
        payment.acquirer
        pos.category
    """)
    util.update_field_references(cr, "image", "image_128", only_models=tuple(other_models))
    util.update_field_references(cr, "image_small", "image_128", only_models=tuple(other_models))
    for model in other_models:
        util.rename_field(cr, model, "image_medium", "image_128")
        util.remove_field(cr, model, "image")
        util.remove_field(cr, model, "image_small")
