# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_field(cr, "rental.wizard", "uom_id", "product_uom_id")

    util.remove_field(cr, "rental.wizard", "name")
