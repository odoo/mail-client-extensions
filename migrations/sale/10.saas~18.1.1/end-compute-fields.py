# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        WITH invoice_totals AS (
            SELECT rel.order_line_id as id, SUM(il.price_total) as total
              FROM sale_order_line_invoice_rel rel
              JOIN account_invoice_line il ON (il.id = rel.invoice_line_id)
              JOIN account_invoice i ON (i.id = il.invoice_id AND i.state IN ('open', 'paid'))
          GROUP BY rel.order_line_id
        ),
        refund_totals AS (
            SELECT rel.order_line_id as id, SUM(r.amount_total) as total
              FROM sale_order_line_invoice_rel rel
              JOIN account_invoice_line il ON (il.id = rel.invoice_line_id)
              JOIN account_invoice i ON (i.id = il.invoice_id AND i.state IN ('open', 'paid'))
              JOIN account_invoice r ON (i.id = r.refund_invoice_id AND r.state IN ('open', 'paid'))
          GROUP BY rel.order_line_id
        ),
        totals AS (
            SELECT i.id, i.total as invoice_total, COALESCE(r.total, 0) as refund_total
              FROM invoice_totals i
         LEFT JOIN refund_totals r ON (i.id = r.id)
        )
        UPDATE sale_order_line l
           SET amt_to_invoice = l.price_total - t.invoice_total,
               amt_invoiced = t.invoice_total - t.refund_total
          FROM totals t
         WHERE t.id = l.id
    """)
    cr.execute("""
        UPDATE sale_order_line
           SET amt_to_invoice = price_total,
               amt_invoiced = 0
         WHERE amt_to_invoice IS NULL
    """)
