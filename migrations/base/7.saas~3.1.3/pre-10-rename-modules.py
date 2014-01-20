# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_module(cr, 'base_calendar', 'calendar')
    util.rename_module(cr, 'google_base_account', 'google_account')
