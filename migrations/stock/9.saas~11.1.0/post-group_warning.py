# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if util.ENVIRON.get('warning_installed'):
        env = util.env(cr)
        cfg = env['stock.config.settings'].create({'group_warning_stock': 1})
        cfg.execute()
