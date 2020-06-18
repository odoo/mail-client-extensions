# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.convert_field_to_property(cr, 'product.template', 'asset_category_id', 'many2one',
                                   target_model='account.asset.category', default_value=None)
    util.convert_field_to_property(cr, 'product.template', 'deferred_revenue_category_id', 'many2one',
                                   target_model='account.asset.category', default_value=None)
    # https://github.com/odoo/odoo/commit/eb8d4aaa59562b41704c715202d0c794fd950a0b#diff-e35933343c229da0afceb2a3b9e3639bL503
    # It's important to remove it, because the field is re-introduced in saas-12.3
    # https://github.com/odoo/enterprise/commit/6cb107c42c1e3a679f7c7b2f41466f39d042bd16#diff-d0dc174b28be71f15f8654cd9a9f5a20R13
    # And it might lead to inconsistencies, adding new depreciation lines to the asset if there are leftovers
    util.remove_field(cr, 'account.move', 'asset_id')
