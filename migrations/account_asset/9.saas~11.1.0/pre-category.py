# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # rename is only relevant in saas-11
    if not util.column_exists(cr, 'account_asset_category', 'account_depreciation_expense_id'):
        util.rename_field(cr, 'account.asset.category',
                          'account_income_recognition_id', 'account_depreciation_expense_id')
    # field now required in saas-11
    # as it was wrongly named (and used) in 9.0, re-map related fields.
    cr.execute("""
        UPDATE account_asset_category
           SET account_depreciation_expense_id = account_asset_id,
               account_asset_id = account_depreciation_id
         WHERE account_depreciation_expense_id IS NULL
    """)
