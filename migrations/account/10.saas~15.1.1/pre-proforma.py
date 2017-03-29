# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
        UPDATE account_invoice
           SET state='draft'
         WHERE state IN ('proforma', 'proforma2')
    """)

    util.remove_record(cr, 'account.group_proforma_invoices')
