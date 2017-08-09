# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    renames = {
        'account.invoice': {
            'invoice_line': 'invoice_line_ids',
            'tax_line': 'tax_line_ids',
            'payment_term': 'payment_term_id',
            'fiscal_position': 'fiscal_position_id',
        }
    }
    for model, ren in renames.items():
        for f, t in ren.items():
            util.rename_field(cr, model, f, t)
