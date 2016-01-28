# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, 'product.variants_template_tree_view',
                          'product.product_attribute_value_view_tree')
    util.rename_xmlid(cr, 'product.variants_template_action',
                          'product.product_attribute_value_action')
