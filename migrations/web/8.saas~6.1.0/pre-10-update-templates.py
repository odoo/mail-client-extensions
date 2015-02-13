# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    for t in 'assets_common assets_backend menu'.split():
        util.force_noupdate(cr, 'web.' + t, False)
