# -*- coding: utf-8 -*-
from openerp.release import series
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # in saas-3, the model pos.category has been renamed to product.public.category and promoted
    # to product module
    # but it's back in saas-5.
    if series not in ('7.saas~3', '7.saas~4'):
        return
    if util.table_exists(cr, 'pos_category'):
        util.rename_model(cr, 'pos.category', 'product.public.category')
        util.move_model(cr, 'product.public.category', 'point_of_sale', 'product')
