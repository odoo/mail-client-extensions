# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    renames = {
        'view_account_analytic_entries_search': 'view_account_analytic_entries_pivot',
        'view_account_entries_report_graph': 'view_account_entries_report_pivot',
        'view_account_invoice_report_graph': 'view_account_invoice_report_pivot',
    }
    for f, t in renames.items():
        util.rename_xmlid(cr, 'account.' + f, 'account.' + t)
