# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    imp = util.import_script("product/saas~12.2.1.2/post-image.py")
    recompute = util.ENVIRON["s125_image_mixin_recompute"]
    for model in recompute["all"]:
        imp.image_mixin_recompute_fields(cr, model)
    for model in recompute["512"]:
        imp.image_mixin_recompute_fields(cr, model, suffixes=["512"])
