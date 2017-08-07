# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_record(cr, 'account.act_account_tax_net')
    util.remove_record(cr, 'account.act_account_tax_tax')
