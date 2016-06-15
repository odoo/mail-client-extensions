# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    config = util.env(cr)['stock.config.settings'].create({})
    config.group_stock_multi_warehouses = config.group_stock_multi_locations
    config.execute()
