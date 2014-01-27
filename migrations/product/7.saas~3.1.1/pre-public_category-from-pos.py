# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance import util

def migrate(cr, version):
    # in saas-3, the model pos.category has been renamed to product.public.category and promoted
    # to product module
    util.rename_model(cr, 'pos.category', 'product.public.category', module='product')
