# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # seems wrong, but it's not. Column name has been fixed
    cr.execute("""
        ALTER TABLE sale_order_line_invoice_rel RENAME COLUMN invoice_id TO invoice_line_id
    """)

    # so_line tax relation table uses the standard table & columns names from now on
    cr.execute("""
        ALTER TABLE sale_order_tax RENAME COLUMN order_line_id TO sale_order_line_id
    """)
    cr.execute("""
        ALTER TABLE sale_order_tax RENAME COLUMN tax_id TO account_tax_id
    """)
    cr.execute("""
        ALTER TABLE sale_order_tax RENAME TO account_tax_sale_order_line_rel
        """)

    # Easier to let the ORM to recreate the whole table instead of droping the bunch of
    # boolean fields that have been converted to 0/1 selection fields.
    cr.execute("DROP TABLE sale_config_settings")

    cr.execute("""
        UPDATE sale_order
            SET state = 'sale'
            WHERE state IN ('waiting_date', 'manual', 'shipping_except', 'invoice_except','progress')
        """)
    cr.execute("UPDATE sale_order_line SET state=so.state FROM sale_order AS so WHERE so.id=order_id")  # field is now related

    # bootstrap some new computed fields
    util.create_column(cr, 'sale_order_line', 'invoice_status', 'varchar')
    util.create_column(cr, 'sale_order_line', 'qty_invoiced', 'numeric')
    util.create_column(cr, 'sale_order_line', 'qty_to_invoice', 'numeric')
    util.create_column(cr, 'sale_order_line', 'qty_delivered', 'numeric')
    util.create_column(cr, 'sale_order_line', 'currency_id', 'int4')
    util.create_column(cr, 'product_template', 'invoice_policy', 'varchar')

    env = util.env(cr)
    order_policy = env['ir.values'].get_default('sale.order', 'order_policy')
    cr.execute("""
        UPDATE product_template
           SET invoice_policy = CASE
                WHEN %s = 'picking' AND type IN ('product', 'consu') THEN 'delivery'
                ELSE 'order'
                END
    """, [order_policy])

    cr.execute("""
        UPDATE sale_order_line l
           SET currency_id = p.currency_id
          FROM sale_order o
          JOIN product_pricelist p ON (p.id = o.pricelist_id)
         WHERE o.id = l.order_id
    """)

    _update_lines(cr)


def _update_lines(cr):
    # update sale order lines fields qty_invoiced, qty_delivered, qty_to_invoice

    # try match order lines to invoice lines with same product (and qty)
    # note: invoice line may receive a discount, so we can't match on it.
    cr.execute("""
        INSERT INTO sale_order_line_invoice_rel(order_line_id, invoice_line_id)
             SELECT ol.id, il.id
               FROM sale_order_line ol
               JOIN sale_order_invoice_rel r ON (r.order_id = ol.order_id)
               JOIN account_invoice_line il ON (r.invoice_id = il.invoice_id)
              WHERE NOT EXISTS(SELECT 1
                                 FROM sale_order_line_invoice_rel
                                WHERE order_line_id = ol.id)
                AND ol.product_id IS NOT NULL
                AND ol.product_id = il.product_id
                AND ol.product_uom_qty = il.quantity
                AND ol.product_uom = il.uom_id
    """)

    cr.execute("""
        UPDATE sale_order_line l
           SET qty_invoiced = round(sign_qty.qty, ceil(-log(uom.rounding))::integer)
          FROM (SELECT sol.id as sol_id,SUM(il.quantity*(CASE WHEN inv.type='out_invoice' THEN 1 ELSE -1 END)) AS qty
                    FROM sale_order_line AS sol,
                         sale_order_line_invoice_rel as rel,
                         account_invoice_line as il,
                         account_invoice as inv
                    WHERE sol.id=rel.order_line_id
                        AND il.id=rel.invoice_line_id
                        AND inv.id=il.invoice_id
                        AND inv.state != 'cancel'
                    GROUP BY sol.id) as sign_qty,
               product_uom uom
         WHERE sign_qty.sol_id = l.id
           AND uom.id = l.product_uom
        """)

    if util.table_exists(cr, 'stock_move'):
        cr.execute("""
            UPDATE sale_order_line l
               SET qty_delivered = round(query.sum, ceil(-log(uom.rounding))::integer)
              FROM (
                    SELECT sol.id, sum(mv.product_qty)
                      FROM stock_move AS mv,
                           stock_location AS loc,
                           procurement_order AS proc,
                           sale_order_line AS sol
                     WHERE mv.location_dest_id=loc.id AND
                           mv.state='done' AND
                           loc.usage='customer' AND
                           loc.scrap_location='f' AND
                           mv.procurement_id=proc.id AND
                           proc.sale_line_id=sol.id
                  GROUP BY sol.id) AS query,
                   product_uom uom
             WHERE query.id = l.id
               AND uom.id = l.product_uom
            """)
        all_moves_done = """
            NOT EXISTS(SELECT 1
                         FROM procurement_order p
                         JOIN stock_move m ON (m.procurement_id = p.id)
                        WHERE p.sale_line_id = l.id
                          AND m.state NOT IN ('done', 'cancel'))
            AND EXISTS(SELECT 1
                         FROM procurement_order p
                         JOIN stock_move m ON (m.procurement_id = p.id)
                        WHERE p.sale_line_id = l.id)
        """
    else:
        cr.execute("UPDATE sale_order_line SET qty_delivered=0")
        all_moves_done = "false"

    cr.execute("""
        UPDATE sale_order_line l
           SET qty_to_invoice = CASE
                WHEN state NOT IN ('sale', 'done') THEN 0
                WHEN EXISTS(SELECT 1
                              FROM product_product p
                              JOIN product_template t ON (t.id = p.product_tmpl_id)
                             WHERE p.id = l.product_id
                               AND t.invoice_policy = 'order')
                THEN round(product_uom_qty - coalesce(qty_invoiced, 0), ceil(-log(uom.rounding))::integer)
                ELSE round(qty_delivered - coalesce(qty_invoiced, 0), ceil(-log(uom.rounding))::integer)
                END
          FROM product_uom uom
         WHERE uom.id = l.product_uom
    """)

    # compute invoice_status field: https://git.io/v2MWu
    cr.execute("""
        UPDATE sale_order_line l
           SET invoice_status = CASE
                WHEN state NOT IN ('sale', 'done') THEN 'no'
                WHEN qty_invoiced IS NULL THEN NULL
                WHEN qty_to_invoice != 0 THEN 'to invoice'
                WHEN (    state = 'sale'
                      AND EXISTS(SELECT 1
                                   FROM product_product p
                                   JOIN product_template t ON (t.id = p.product_tmpl_id)
                                  WHERE p.id = l.product_id
                                    AND t.invoice_policy = 'order')
                      AND qty_delivered > product_uom_qty) THEN 'upselling'
                WHEN (
                      {all_moves_done}
                      AND state = 'done'
                      AND EXISTS(SELECT 1
                                   FROM product_product p
                                   JOIN product_template t ON (t.id = p.product_tmpl_id)
                                  WHERE p.id = l.product_id
                                    AND t.invoice_policy = 'delivery'
                                    AND t.type IN ('consu', 'product'))
                      ) THEN 'invoiced'
                WHEN qty_invoiced >= product_uom_qty THEN 'invoiced'
                ELSE 'no'
                END
        """.format(all_moves_done=all_moves_done))

    # in 8.0, there use to be a m2m sale.order <=> account.invoice
    # Now, only the m2m sale.order.line <=> account.invoice.line is used to find the invoices
    # linked to a sale.order
    # However this m2m does not always contains the correct links
    # This will cause the field `qty_invoiced` to be NULL (undermined).
    # Try to guess if SO is fully paid by comparing invoice amounts

    cr.execute("""
        WITH sol_inv AS (
            SELECT l.id, o.amount_total, pl.currency_id, o.date_order, o.company_id,
                   array_agg(r.invoice_id) AS invoices
              FROM sale_order_line l
              JOIN sale_order o ON (o.id = l.order_id)
              JOIN sale_order_invoice_rel r ON (r.order_id = l.order_id)
              JOIN product_pricelist pl ON (pl.id = o.pricelist_id)
             WHERE l.invoice_status IS NULL
          GROUP BY l.id, o.amount_total, pl.currency_id, o.date_order, o.company_id
        ),
        _upd AS (
            UPDATE sale_order_line l
               SET invoice_status = 'invoiced'
              FROM sol_inv s
             WHERE s.id = l.id
               AND NOT EXISTS(
                    SELECT 1
                      FROM account_invoice
                     WHERE id = ANY(s.invoices)
                       AND (state NOT IN ('paid', 'cancel') OR currency_id != s.currency_id)
               )
               AND s.amount_total <= (SELECT SUM(amount_total)
                                        FROM account_invoice
                                       WHERE state = 'paid'
                                         AND currency_id = s.currency_id
                                         AND id = ANY(s.invoices))
        )
        SELECT s.id, s.amount_total, s.currency_id, s.date_order, s.company_id, s.invoices
          FROM sol_inv s
          JOIN sale_order_line l ON (l.id = s.id)
         WHERE l.invoice_status IS NULL
           AND NOT EXISTS(
                SELECT 1
                  FROM account_invoice
                 WHERE id = ANY(s.invoices)
                   AND state NOT IN ('paid', 'cancel')
           )
           AND EXISTS(
                SELECT 1
                  FROM account_invoice
                 WHERE id = ANY(s.invoices)
                   AND state = 'paid'
                   AND currency_id != s.currency_id)

    """)
    invoiced = []
    env = util.env(cr)
    Currency = env['res.currency']
    for sol_id, amount_total, currency_id, order_date, company_id, invoice_ids in cr.fetchall():
        cur_t = Currency.browse(currency_id).with_context(company_id=company_id, date=order_date)
        total = 0.0
        cr.execute("""
            SELECT amount_total, currency_id, date_invoice, company_id
              FROM account_invoice
             WHERE id IN %s
               AND state = 'paid'
        """, [tuple(invoice_ids)])
        for inv_total, inv_currency_id, inv_date, inv_company_id in cr.fetchall():
            if inv_currency_id == currency_id:
                total += inv_total
            else:
                cur_f = Currency.browse(inv_currency_id)
                cur_f = cur_f.with_context(company_id=inv_company_id, date=inv_date)
                total += cur_f.compute(inv_total, cur_t, round=False)
        if cur_t.compare_amounts(amount_total, total) <= 0:
            invoiced.append(sol_id)

    if invoiced:
        cr.execute("UPDATE sale_order_line SET invoice_status='invoiced' WHERE id IN %s",
                   [tuple(invoiced)])

    cr.execute("UPDATE sale_order_line SET invoice_status='to invoice' WHERE invoice_status IS NULL")

    # Link every order line with every invoice line of linked invoice
    cr.execute("""
        INSERT INTO sale_order_line_invoice_rel(order_line_id, invoice_line_id)
             SELECT ol.id, il.id
               FROM sale_order_line ol
               JOIN sale_order_invoice_rel r ON (r.order_id = ol.order_id)
               JOIN account_invoice_line il ON (r.invoice_id = il.invoice_id)
              WHERE NOT EXISTS(SELECT 1
                                 FROM sale_order_line_invoice_rel
                                WHERE order_line_id = ol.id)
    """)


def main(cr, version):
    # main function, to be called on already migrated databases
    cr.execute("UPDATE sale_order_line SET qty_invoiced=NULL")
    _update_lines(cr)
    cr.execute("""
        UPDATE sale_order o
           SET invoice_status =
                CASE WHEN state NOT IN ('sale', 'done') THEN 'no'
                     WHEN EXISTS(SELECT 1
                                   FROM sale_order_line
                                  WHERE order_id=o.id
                                    AND invoice_status='to invoice') THEN 'to invoice'
                    WHEN NOT EXISTS(SELECT 1
                                      FROM sale_order_line
                                     WHERE order_id=o.id
                                       AND invoice_status != 'invoiced') THEN 'invoiced'
                    WHEN NOT EXISTS(SELECT 1
                                      FROM sale_order_line
                                     WHERE order_id=o.id
                                       AND invoice_status NOT IN ('invoiced', 'upselling')) THEN 'upselling'
                    ELSE 'no'
                    END
    """)

if __name__ == '__main__':
    util.main(main)
