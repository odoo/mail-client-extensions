# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    image = util.import_script("base/saas~12.5.1.3/pre-21-images.py")
    image.rename_mixin_fields(cr, "slide.channel")
    image.rename_mixin_fields(cr, "slide.slide")
