# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.recompute_fields(cr, "account.asset", ["non_deductible_tax_val"])
