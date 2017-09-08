# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_field(cr, 'sale.config.settings', 'module_sale_contract', 'module_sale_subscription')
