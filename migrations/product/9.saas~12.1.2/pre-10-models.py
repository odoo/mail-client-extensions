# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'product.category', 'sequence')
    util.remove_field(cr, 'product.product', 'name_template')
