# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.move_model(cr, "iot.trigger", "iot", "mrp_workorder_iot")
