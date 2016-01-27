# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    m = util.import_script('account/9.0.1.1/post-91-recompute-invoice-tax.py')
    m.update_invoice_taxes(cr)
