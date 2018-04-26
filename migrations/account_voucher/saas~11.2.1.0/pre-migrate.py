# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'account_voucher', 'company_id', 'int4')
    util.create_column(cr, 'account_voucher', 'currency_id', 'int4')

    cr.execute("""
        UPDATE account_voucher v
           SET company_id = j.company_id,
               currency_id = COALESCE(j.currency_id, c.currency_id)
          FROM account_journal j, res_company c
         WHERE j.id = v.journal_id
           AND c.id = j.company_id
    """)
