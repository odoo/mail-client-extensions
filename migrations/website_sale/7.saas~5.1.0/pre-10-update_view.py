#-*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_record(cr, 'website_sale.product')
    util.remove_record(cr, 'website_sale.view_sales_config_website_sale')
