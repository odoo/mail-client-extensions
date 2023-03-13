# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.module_installed(cr, "mrp_workorder_iot"):
        util.move_model(cr, "iot.trigger", "iot", "mrp_workorder_iot")
    else:
        util.remove_model(cr, "iot.trigger")
