# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    image = util.import_script("base/saas~12.5.1.3/pre-21-images.py")
    image.single_image(cr, "fleet.vehicle")
    image.single_image(cr, "fleet.vehicle.model")
    image.single_image(cr, "fleet.vehicle.model.brand")
