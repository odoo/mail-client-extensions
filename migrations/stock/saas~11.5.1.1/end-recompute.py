# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Necessary because translation is removed from stock.location.name
    # Check if multiple languages are installed befre triggering the recompute?
    util.recompute_fields(cr, "stock.location", ["complete_name"])
