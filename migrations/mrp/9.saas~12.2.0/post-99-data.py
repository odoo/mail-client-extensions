# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Force data to not be removed
    util.force_noupdate(cr, "mrp.picking_type_manufacturing", True)
