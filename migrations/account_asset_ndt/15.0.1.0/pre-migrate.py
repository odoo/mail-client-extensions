# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_asset", "non_deductible_tax_val", "numeric")
