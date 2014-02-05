# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # in saas-3, the model pos.category has been renamed to product.public.category and promoted
    # to product module
    if util.table_exists(cr, 'pos_category'):
        util.rename_model(cr, 'pos.category', 'product.public.category', module='product')
