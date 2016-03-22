# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.move_field_to_module(cr, 'sale.order', 'validity_date', 'website_quote', 'sale')

