# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'base.config.settings', 'group_product_variant')
    util.remove_record(cr, 'product.group_mrp_properties')
