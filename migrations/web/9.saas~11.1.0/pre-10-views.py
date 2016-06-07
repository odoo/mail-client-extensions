# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.force_noupdate(cr, 'web.layout', False)
    util.force_noupdate(cr, 'web.menu_secondary', False)
    util.force_noupdate(cr, 'web.webclient_bootstrap', False)
