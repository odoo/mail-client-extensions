# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_asset", "non_deductible_tax_value", "numeric", default=0.0)

    util.remove_view(cr, "account_asset.asset_sell_form")
    util.remove_view(cr, "account_asset.asset_pause_form")

    util.remove_model(cr, "account.asset.sell")
    util.remove_model(cr, "account.asset.pause")
