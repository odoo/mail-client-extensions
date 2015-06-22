# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    xids = {
        'crm.crm_case_channel_website': 'crm.crm_medium_website',
        'crm.crm_case_channel_phone': 'crm.crm_medium_phone',
        'crm.crm_case_channel_direct': 'crm.crm_medium_direct',
        'crm.crm_case_channel_email': 'crm.crm_medium_email',
    }

    for o, n in xids.items():
        util.rename_xmlid(cr, o, n)
