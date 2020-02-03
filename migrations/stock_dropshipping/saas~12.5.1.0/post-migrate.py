# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    C = util.env(cr)["res.company"]
    C.create_missing_dropship_sequence()
    C.create_missing_dropship_picking_type()
    C.create_missing_dropship_rule()
