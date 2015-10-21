# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    for t in 'assets_common assets_backend menu'.split():
        util.force_noupdate(cr, 'web.' + t, False)

    # reset backend asset for other web_* modules (no need to create 1 line migreation scripts)
    for m in 'calendar diagram gantt kanban tip'.split():
        util.force_noupdate(cr, 'web_%s.assets_backend' % m, False)
