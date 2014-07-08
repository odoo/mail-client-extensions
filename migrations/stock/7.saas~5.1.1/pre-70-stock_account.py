# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # as stock_account is a new module, no migration will be executed, steal xmlids here
    xids = """
        stock_journal_sequence
        stock_journal
        group_inventory_valuation
        group_stock_inventory_valuation
    """.split()
    for x in xids:
        util.rename_xmlid(cr, 'stock.' + x, 'stock_account.' + x)
