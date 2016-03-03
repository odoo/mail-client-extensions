# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    views = util.splitlines("""
        category_template
        subtotal_template
        separator_template
        report_sale_layouted
        report_invoice_layouted
    """)
    for v in views:
        util.force_noupdate(cr, 'sale_layout.' + v, False)
