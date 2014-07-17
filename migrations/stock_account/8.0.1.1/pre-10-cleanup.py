# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    table = 'stock_invoice_onshipping'
    if util.table_exists(cr, table):
        # as this is a TransientModel, it doesn't worth migrating data.
        cr.execute("DELETE FROM " + table)
