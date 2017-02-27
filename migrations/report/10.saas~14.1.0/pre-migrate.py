# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(
        cr, *util.expand_braces('{account_batch_deposit,report}.paperformat_batch_deposit'))
