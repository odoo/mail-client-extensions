#-*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_record(cr, 'website_sale.product')
    util.remove_record(cr, 'website_sale.view_sales_config_website_sale')

    # Shop templates need to be reset - they're not compatible anymore
    util.force_noupdate(cr, 'website_sale.products', False)
    util.force_noupdate(cr, 'website_sale.categories_recursive', False)
    util.force_noupdate(cr, 'website_sale.products_categories', False)
    util.force_noupdate(cr, 'website_sale.search', False)