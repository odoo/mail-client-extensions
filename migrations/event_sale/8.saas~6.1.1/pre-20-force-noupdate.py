# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.force_noupdate(cr, 'event_sale.event_type')
    util.force_noupdate(cr, 'event_sale.product_product_event')
    util.force_noupdate(cr, 'event_sale.product_product_event_product_template')
