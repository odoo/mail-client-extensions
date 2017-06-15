# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    env = util.env(cr)
    env.ref('gamification.goal_user_visibility').groups += env.ref('base.group_portal')
