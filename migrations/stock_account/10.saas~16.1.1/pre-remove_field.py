# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'stock.config.settings', 'group_stock_inventory_valuation')
    util.remove_record(cr, 'stock_account.group_inventory_valuation')
