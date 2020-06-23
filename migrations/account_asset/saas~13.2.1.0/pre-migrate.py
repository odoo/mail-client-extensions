# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "account_asset", "value_residual")  # now computed
    util.create_column(cr, "account_asset", "already_deprecated_amount_import", "numeric")
    util.create_column(cr, "account_asset", "depreciation_number_import", "integer")
    util.create_column(cr, "account_asset", "first_depreciation_date_import", "date")
