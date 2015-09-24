# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    env = util.env(cr)
    env['sale.config.settings'].create({'group_use_lead': 1}).execute()
