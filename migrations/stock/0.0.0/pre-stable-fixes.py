# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("14.0", "17.0"):
        # non-stored field remove in stable version.
        # See https://github.com/odoo/odoo/pull/120048
        util.remove_field(cr, "report.stock.quantity", "move_ids")
