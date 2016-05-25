# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    fields = ['price_tax', 'price_subtotal', 'price_total']
    # FIXME finetune `chunk_size`
    util.recompute_fields(cr, 'sale.order.line', fields, chunk_size=42)
