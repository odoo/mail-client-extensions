# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("DROP TABLE stock_config_settings")
    for v in 'view_move_form view_move_picking_form assets_backend'.split():
        util.force_noupdate(cr, 'stock.' + v, False)
