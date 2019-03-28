# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    imp = util.import_script("product/saas~12.2.1.2/post-image.py")
    imp.image_mixin_recompute_fields(cr, "product.image")
