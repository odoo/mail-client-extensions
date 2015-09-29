# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.force_noupdate(cr, 'website_sale.cart', False)
    util.force_noupdate(cr, 'website_sale.total', False)
