# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_record(cr, 'website_sale.view_sales_config_website_sale')

    # Shop templates need to be reset - they're not compatible anymore
    cr.execute("""UPDATE ir_model_data
                     SET name='product_comment'
                   WHERE model='website_sale'
                     AND name='product_option_openchatter'
               """)

    util.force_noupdate(cr, 'website_sale.product', False)

    util.force_noupdate(cr, 'website_sale.product_description', False)

    # remove inherited views of 'website_sale.products'
    for v in 'list_view products_categories products_attributes'.split():
        util.remove_record(cr, 'website_sale.%s' % v)

    util.force_noupdate(cr, 'website_sale.products', False)

    util.force_noupdate(cr, 'website_sale.categories_recursive', False)
    util.force_noupdate(cr, 'website_sale.search', False)
