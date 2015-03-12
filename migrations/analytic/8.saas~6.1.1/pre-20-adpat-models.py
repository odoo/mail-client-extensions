# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.drop_depending_views(cr, 'account_analytic_account', 'state')
    util.drop_depending_views(cr, 'account_analytic_journal', 'type')
