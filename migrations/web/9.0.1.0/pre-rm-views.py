# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_view(cr, 'web.layout')
    util.force_noupdate(cr, 'web.login', False)
    util.force_noupdate(cr, 'web.webclient_bootstrap', False)
