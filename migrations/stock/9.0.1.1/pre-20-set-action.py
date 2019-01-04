# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # force empty src_model; see #277
    cr.execute("UPDATE ir_act_window SET src_model = NULL WHERE id = %s",
               [util.ref("stock.action_procurement_compute")])
