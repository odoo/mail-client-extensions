# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.delete_model(cr, 'sale.receipt.report')
    util.create_column(cr, 'account_voucher_line', 'price_subtotal', 'float8')
