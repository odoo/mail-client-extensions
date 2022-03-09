# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    if util.column_exists(cr, "account_asset", "non_deductible_tax_val"):
        util.rename_field(cr, "account.asset", "non_deductible_tax_val", "non_deductible_tax_value")
    else:
        # The column should not be computed for existing records, hence the default value.
        util.create_column(cr, "account_asset", "non_deductible_tax_value", "numeric", default=0.0)

    util.remove_view(cr, "account_asset.asset_sell_form")
    util.remove_view(cr, "account_asset.asset_pause_form")

    util.remove_model(cr, "account.asset.sell")
    util.remove_model(cr, "account.asset.pause")
