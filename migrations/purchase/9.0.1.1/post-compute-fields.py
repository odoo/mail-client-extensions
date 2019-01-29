# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    POL = util.env(cr)["purchase.order.line"].with_context(**{"raise-exception": False})
    util.recompute_fields(cr, POL, ["qty_invoiced", "qty_received"])
