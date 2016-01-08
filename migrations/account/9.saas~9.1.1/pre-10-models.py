# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.move_field_to_module(cr, 'res.partner', 'trust', 'account_reports_followup', 'account')
    util.rename_xmlid(cr, 'account_reports_followup.default_followup_trust', 'account.default_followup_trust')
