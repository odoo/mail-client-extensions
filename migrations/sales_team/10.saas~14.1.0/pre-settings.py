# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_view(cr, 'sales_team.view_sale_config_settings')
    util.move_field_to_module(cr,
                              'sale.config.settings', 'module_website_sign',
                              'crm', 'sales_team')
