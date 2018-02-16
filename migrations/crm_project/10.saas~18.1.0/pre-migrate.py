# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_model(cr, 'crm.lead2projectissue.wizard', 'crm.lead.convert2task')
