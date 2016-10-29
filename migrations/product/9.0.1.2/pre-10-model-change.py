# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.delete_model(cr, 'product.ul')
    util.delete_model(cr, 'pricelist.partner_info')
