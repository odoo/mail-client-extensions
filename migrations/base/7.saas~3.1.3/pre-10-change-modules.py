# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_module(cr, 'base_calendar', 'calendar')
    util.rename_module(cr, 'google_base_account', 'google_account')

    util.new_module_dep(cr, 'calendar', 'web_calendar')

    util.remove_module(cr, 'web_shortcuts')
