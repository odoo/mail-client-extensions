# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
        SELECT id
          FROM hr_expense
         WHERE currency_company_id IS NOT NULL
           AND total_amount_company IS NULL
    """)
    ids = [x[0] for x in cr.fetchall()]
    util.recompute_fields(cr, 'hr.expense', ['total_amount_company'], ids=ids)
