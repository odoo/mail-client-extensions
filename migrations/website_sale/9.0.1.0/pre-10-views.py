# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    views = "cart total product_item product suggested_products_list extra_info reduction_code checkout payment".split()
    for v in views:
        util.force_noupdate(cr, 'website_sale.' + v, False)

    util.remove_view(cr, 'website_sale.variants_template_tree_view')
