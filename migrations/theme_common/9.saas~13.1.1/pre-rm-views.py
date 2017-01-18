# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    for t in 'anelusia kea loftspace monglia'.split():
        util.remove_view(cr, 'theme_%s.font_size' % t)
