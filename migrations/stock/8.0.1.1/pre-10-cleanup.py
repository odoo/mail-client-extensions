# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # NOTE this script belong to `stock_account` module, but as this is a new module, when
    #      migrating from < saas-5, the script will not be called. Force call by placing it here.

    table = 'stock_invoice_onshipping'
    if util.table_exists(cr, table):
        # as this is a TransientModel, it doesn't worth migrating data.
        cr.execute("DELETE FROM " + table)
