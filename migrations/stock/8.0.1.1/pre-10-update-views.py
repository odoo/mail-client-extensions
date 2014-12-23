# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # NOTE: it should be in stock_account (since SaaS 4) but we don't bother to
    #       move the view to stock_account since it disappears in Odoo 8.0
    util.remove_view(cr, 'stock.view_product_standard_price_form')
