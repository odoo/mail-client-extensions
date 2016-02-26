# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    meth_in = util.ref(cr, 'account.account_payment_method_manual_in')
    meth_out = util.ref(cr, 'account.account_payment_method_manual_out')

    util.create_column(cr, 'account_payment', '_voucher_id', 'int4')
    cr.execute("""
        INSERT INTO account_payment(
            _voucher_id, create_uid, create_date, write_uid, write_date,
            payment_type, name, state, partner_id, partner_type, journal_id, payment_method_id,
            amount, currency_id, payment_date, payment_reference, communication, company_id,
            payment_difference_handling, writeoff_account_id
        )

        SELECT id,
               create_uid, create_date, write_uid, write_date,
               CASE WHEN amount < 0 THEN 'outbound' ELSE 'inbound' END,
               COALESCE(number, name),
               CASE WHEN state != 'posted' THEN 'draft'
                    WHEN EXISTS(SELECT 1
                                  FROM account_move_line
                                 WHERE move_id = v.move_id
                                   AND statement_id IS NOT NULL) THEN 'reconciled'
                    ELSE 'posted'
               END,
               partner_id,
               CASE WHEN type='payment' THEN 'supplier' ELSE 'customer' END,
               journal_id,
               CASE WHEN amount < 0 THEN
                    (SELECT COALESCE(
                        (SELECT outbound_payment_method
                           FROM account_journal_outbound_payment_method_rel
                          WHERE journal_id=v.journal_id
                          LIMIT 1), %s))
                 ELSE
                    (SELECT COALESCE(
                        (SELECT inbound_payment_method
                           FROM account_journal_inbound_payment_method_rel
                          WHERE journal_id=v.journal_id
                          LIMIT 1), %s))
               END,
               abs(amount),
               (SELECT COALESCE(j.currency_id, c.currency_id)
                  FROM account_journal j JOIN res_company c ON (c.id = j.company_id)
                 WHERE j.id = v.journal_id),
               date,
               reference,
               narration,
               company_id,
               CASE WHEN payment_option='without_writeoff' THEN 'open' ELSE 'reconcile' END,
               writeoff_acc_id

          FROM account_voucher v
         WHERE type IN ('payment', 'receipt')
      ORDER BY id
    """, [meth_out, meth_in])

    cr.execute("""
        UPDATE account_move_line l
           SET payment_id = p.id
          FROM account_voucher v, account_payment p
         WHERE v.type IN ('payment', 'receipt')
           AND v.move_id = l.move_id
           AND v.id = p._voucher_id
           -- AND (l.debit = p.amount OR l.credit = p.amount)
    """)
    cr.execute("""
        INSERT INTO account_invoice_payment_rel(payment_id, invoice_id)
             SELECT payment_id, invoice_id
               FROM account_move_line
              WHERE payment_id IS NOT NULL
                AND invoice_id IS NOT NULL
    """)

    cr.execute("ALTER TABLE account_payment DROP COLUMN _voucher_id")

    cr.execute("DELETE FROM account_voucher WHERE type NOT IN ('sale', 'purchase')")
