# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.force_noupdate(cr, 'point_of_sale.index', False)
    cr.execute("DROP TABLE IF EXISTS pos_config_settings")
    util.drop_view(cr, 'point_of_sale.view_sale_config_settings_form_pos')
