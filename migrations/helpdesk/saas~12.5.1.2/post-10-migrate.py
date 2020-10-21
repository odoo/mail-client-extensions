# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.recompute_fields(cr, "helpdesk.sla.status", ["deadline", "exceeded_days"])
