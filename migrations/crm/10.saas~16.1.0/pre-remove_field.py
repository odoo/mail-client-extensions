# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'crm.lead', 'date_action_next')
    util.remove_field(cr, 'res.partner', 'activities_count')
