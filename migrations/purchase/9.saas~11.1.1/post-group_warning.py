# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if util.ENVIRON.get('warning_installed'):
        env = util.env(cr)
        cfg = env['purchase.config.settings'].create({'group_warning_purchase': 1})
        cfg.execute()
