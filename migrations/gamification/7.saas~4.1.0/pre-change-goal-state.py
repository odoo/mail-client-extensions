# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'gamification_goal', 'to_update', 'boolean')
    cr.execute("UPDATE gamification_goal SET to_update=%s", (False,))
    cr.execute("UPDATE gamification_goal SET state=%s, to_update=%s WHERE state=%s",
               ('inprogress', True, 'inprogress_update'))
