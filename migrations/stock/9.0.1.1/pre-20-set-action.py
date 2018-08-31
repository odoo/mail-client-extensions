# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # src_model value was dropped
    env = util.env(cr)
    action = env.ref('stock.action_procurement_compute', raise_if_not_found=False)
    if action:
        action.write({'src_model': False})
