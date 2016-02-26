# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.force_noupdate(cr, 'point_of_sale.index', False)
    cr.execute("DROP TABLE IF EXISTS pos_config_settings")
    for view in "view_sale_config_settings_form_pos product_template_form_view_inherit_ean product_normal_form_view_inherit_ean".split():
        util.remove_view(cr, "point_of_sale." + view)
