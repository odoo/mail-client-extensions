# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # templates were not translated as no language specified
    # fixed at 2acad60 but requires manual update
    util.force_noupdate(cr, 'gamification.email_template_badge_received', False)
    util.force_noupdate(cr, 'gamification.email_template_goal_reminder', False)
