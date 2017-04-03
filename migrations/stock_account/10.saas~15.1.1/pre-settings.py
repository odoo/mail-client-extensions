# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'stock.config.settings', 'group_stock_inventory_valuation')
    util.remove_field(cr, 'stock.config.settings', 'module_stock_landed_costs')
    util.force_noupdate(cr, 'stock_account.view_stock_config_settings_inherit', False)
