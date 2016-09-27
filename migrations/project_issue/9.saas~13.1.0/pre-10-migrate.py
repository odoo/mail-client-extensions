# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    for mode in 'kanban tree calendar form graph'.split():
        util.remove_record(cr, 'project.action_crm_tag_%s_view0' % mode)
