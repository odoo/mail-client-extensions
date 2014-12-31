# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, 'sale_crm.account_invoice_groupby_inherit',
                              'sale.account_invoice_groupby_inherit')
