# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, 'account_followup.view_account_followup_stat_graph',
                          'account_followup.view_account_followup_stat_pivot')
