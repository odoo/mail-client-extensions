# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.recompute_fields(cr, 'repair.line', ['price_subtotal'])
    util.recompute_fields(cr, 'repair.fee', ['price_subtotal'])
