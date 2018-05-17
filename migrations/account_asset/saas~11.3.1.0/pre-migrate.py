# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_asset_category", "date_first_depreciation", "varchar")
    cr.execute("UPDATE account_asset_category SET date_first_depreciation='manual'")

    util.create_column(cr, "account_asset_asset", "date_first_depreciation", "varchar")
    util.create_column(cr, "account_asset_asset", "first_depreciation_manual_date", "date")
    cr.execute("""
        UPDATE account_asset_asset
           SET date_first_depreciation = 'manual',
               first_depreciation_manual_date = date
    """)
