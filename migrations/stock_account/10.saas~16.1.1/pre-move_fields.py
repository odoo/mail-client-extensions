# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if util.module_installed(cr, 'sale_stock'):
        for m in 'stock.move stock.return.picking.line'.split():
            util.move_field_to_module(cr, m, 'to_refund_so', 'sale_stock', 'stock_account')
            util.rename_field(cr, m, 'to_refund_so', 'to_refund')
