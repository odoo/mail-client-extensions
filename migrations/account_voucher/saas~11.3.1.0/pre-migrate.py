# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'account_voucher', 'payment_journal_id', 'int4')
    cr.execute("""
          WITH cte AS (
            SELECT v.id, v.account_id, a.internal_type
              FROM account_voucher v
         LEFT JOIN account_account a ON (a.id = v.account_id)
             WHERE v.pay_now = 'pay_now'
          )

        UPDATE account_voucher v
           SET payment_journal_id = j.id
          FROM cte, account_journal j
         WHERE v.id = cte.id
           AND j.type IN ('bank', 'cash')
           AND j.company_id = v.company_id
           AND (   cte.internal_type != 'liquidity'
                OR CASE WHEN v.voucher_type = 'sale'
                        THEN j.default_debit_account_id = cte.account_id
                        ELSE j.default_credit_account_id = cte.account_id
                    END)
    """)
