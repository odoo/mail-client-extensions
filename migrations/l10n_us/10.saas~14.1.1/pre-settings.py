# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'account.config.settings', 'module_account_taxcloud')
