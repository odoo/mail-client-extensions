# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        UPDATE account_invoice r
           SET refund_invoice_id = i.id
          FROM account_invoice i
         WHERE r.type IN ('out_refund', 'in_refund')
           AND i.type IN ('out_invoice', 'in_invoice')
           AND r.origin = i.number
           AND r.company_id = i.company_id
           AND r.partner_id = i.partner_id
    """)
