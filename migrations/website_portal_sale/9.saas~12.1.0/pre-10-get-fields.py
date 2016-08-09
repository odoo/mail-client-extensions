# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.move_field_to_module(cr, 'payment.transaction', 'sale_order_id',
                              'website_sale', 'website_portal_sale')
