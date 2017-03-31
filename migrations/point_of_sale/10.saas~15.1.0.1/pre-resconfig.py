# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    for module in 'restaurant loyalty discount mercury reprint'.split():
        util.remove_field(cr, 'pos.config.settings', 'module_pos_' + module)
    util.remove_view(cr, 'point_of_sale.view_sale_config_settings_form_pos')
