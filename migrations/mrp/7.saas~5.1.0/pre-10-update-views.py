# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_view(cr, 'mrp.product_product_normal_form_supply_view')
    util.rename_xmlid(cr,         'mrp.product_form_view_bom_button',
                          'mrp.product_product_form_view_bom_button')
