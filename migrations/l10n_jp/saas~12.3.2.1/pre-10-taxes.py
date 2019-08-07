# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if util.table_exists(cr, 'financial_report_lines_v12_bckp'):
        # Some financial report lines have a domain, but no formula; we give them one
        cr.execute("""
            update financial_report_lines_v12_bckp
            set formulas = 'balance = sum.balance'
            where domain is not null
            and formulas is null;
        """)
