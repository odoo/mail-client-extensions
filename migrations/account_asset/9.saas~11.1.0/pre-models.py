# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.convert_field_to_property(cr, 'product.template', 'asset_category_id', 'many2one',
                                   target_model='account.asset.category', default_value=None)
    util.convert_field_to_property(cr, 'product.template', 'deferred_revenue_category_id', 'many2one',
                                   target_model='account.asset.category', default_value=None)
