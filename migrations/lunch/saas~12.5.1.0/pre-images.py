# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # NOTE model `lunch.product.category` has also the mixin, but has no existing image fields to rename
    util.import_script("base/saas~12.5.1.3/pre-21-images.py").new_inherit_mixin(cr, "lunch.product")
