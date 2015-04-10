# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_model(cr, 'crm.case.channel', 'crm.tracking.medium')
    util.rename_model(cr, 'crm.case.resource.type', 'crm.tracking.campaign')

    util.rename_field(cr, 'crm.lead', 'type_id', 'campaign_id')
