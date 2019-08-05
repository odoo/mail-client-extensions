# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'account_invoice', 'activity_date_deadline', 'date')
    util.create_column(cr, "account_invoice_tax", "base", "numeric")
