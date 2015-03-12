# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.drop_depending_views(cr, 'marketing_campaign_workitem', 'state')
