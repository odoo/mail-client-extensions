# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.force_noupdate(cr, 'website_sale.product_attribute_value_view_tree_inherit_website_sale',
                        False)
    util.force_noupdate(cr, 'website_sale.variants_tree_view', False)
