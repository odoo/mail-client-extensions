# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.convert_field_to_property(cr, 'product.template', 'standard_price', 'float',
                                   default_value=0)
