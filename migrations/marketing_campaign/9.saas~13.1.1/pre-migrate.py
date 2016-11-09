# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.drop_workflow(cr, 'marketing.campaign')
    util.drop_workflow(cr, 'marketing.campaign.segment')
    util.rename_field(cr, 'marketing.campaign.activity', 'type', 'action_type')
