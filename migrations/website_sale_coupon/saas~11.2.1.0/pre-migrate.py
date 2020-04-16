# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'sale.coupon.rule', 'is_public_included')
    # sale.coupon.program inheritS of sale.coupon.rule
    util.remove_field(cr, 'sale.coupon.program', 'is_public_included', drop_column=False)
