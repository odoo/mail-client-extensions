# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # seems wrong, but it's not. Column name has been fixed
    cr.execute(
        """
        ALTER TABLE sale_order_line_invoice_rel RENAME COLUMN invoice_id TO invoice_line_id
    """
    )

    # so_line tax relation table uses the standard table & columns names from now on
    cr.execute(
        """
        ALTER TABLE sale_order_tax RENAME COLUMN order_line_id TO sale_order_line_id
    """
    )
    cr.execute(
        """
        ALTER TABLE sale_order_tax RENAME COLUMN tax_id TO account_tax_id
    """
    )
    cr.execute(
        """
        ALTER TABLE sale_order_tax RENAME TO account_tax_sale_order_line_rel
        """
    )

    util.rename_field(cr, "sale.order", "payment_term", "payment_term_id")
    util.rename_field(cr, "sale.order", "fiscal_position", "fiscal_position_id")
    report = util.ref(cr, "sale.report_saleorder_document")
    if report:
        cr.execute(
            """
            UPDATE ir_ui_view
               SET arch_db = replace(arch_db, 'o.payment_term', 'o.payment_term_id')
             WHERE id = %s
        """,
            [report],
        )

    # Easier to let the ORM to recreate the whole table instead of droping the bunch of
    # boolean fields that have been converted to 0/1 selection fields.
    cr.execute("DROP TABLE sale_config_settings")

    cr.execute(
        """
        UPDATE sale_order
            SET state = 'sale'
            WHERE state IN ('waiting_date', 'manual', 'shipping_except', 'invoice_except','progress')
        """
    )
    cr.execute(
        "UPDATE sale_order_line sl SET state=so.state FROM sale_order AS so WHERE so.id=sl.order_id"
    )  # field is now related

    # bootstrap some new computed fields
    util.create_column(cr, "sale_order", "invoice_status", "varchar")
    util.create_column(cr, "sale_order_line", "invoice_status", "varchar")
    util.create_column(cr, "sale_order_line", "qty_invoiced", "numeric")
    util.create_column(cr, "sale_order_line", "qty_to_invoice", "numeric")
    util.create_column(cr, "sale_order_line", "qty_delivered", "numeric")
    util.create_column(cr, "sale_order_line", "currency_id", "int4")
    util.create_column(cr, "product_template", "invoice_policy", "varchar")

    env = util.env(cr)
    order_policy = env["ir.values"].get_default("sale.order", "order_policy")
    cr.execute(
        """
        UPDATE product_template
           SET invoice_policy = CASE
                WHEN %s = 'picking' AND type IN ('product', 'consu') THEN 'delivery'
                ELSE 'order'
                END
    """,
        [order_policy],
    )

    # set default order policy
    if order_policy == "picking":
        env["ir.values"].set_default("product.template", "invoice_policy", "delivery")

    cr.execute(
        """
        UPDATE sale_order_line l
           SET currency_id = p.currency_id
          FROM sale_order o
          JOIN product_pricelist p ON (p.id = o.pricelist_id)
         WHERE o.id = l.order_id
    """
    )

    _update_lines(cr)


def _update_lines(cr):
    # update sale order lines fields qty_invoiced, qty_delivered, qty_to_invoice

    # try match order lines to invoice lines with same product (and qty)
    # note: invoice line may receive a discount, so we can't match on it.
    cr.execute(
        """
        INSERT INTO sale_order_line_invoice_rel(order_line_id, invoice_line_id)
             SELECT ol.id, il.id
               FROM sale_order_line ol
               JOIN sale_order_invoice_rel r ON (r.order_id = ol.order_id)
               JOIN account_invoice_line il ON (r.invoice_id = il.invoice_id)
               JOIN product_uom ol_uom ON (ol_uom.id = ol.product_uom)
               JOIN product_uom il_uom ON (il_uom.id = il.uom_id)
              WHERE NOT EXISTS(SELECT 1
                                 FROM sale_order_line_invoice_rel
                                WHERE order_line_id = ol.id)
                AND ol.product_id IS NOT NULL
                AND ol.product_id = il.product_id
                AND ol.invoiced = 't'
                AND ol_uom.category_id = il_uom.category_id
    """
    )

    cr.execute(
        """
        UPDATE sale_order_line l
           SET qty_invoiced = round(sign_qty.qty, ceil(-log(uom.rounding))::integer)
          FROM (SELECT sol.id as sol_id,
                       SUM(
                         il.quantity / il_uom.factor * sol_uom.factor * (CASE WHEN inv.type='out_invoice' THEN 1 ELSE -1 END)
                       ) AS qty
                  FROM sale_order_line AS sol
                  JOIN sale_order_line_invoice_rel rel ON (rel.order_line_id = sol.id)
                  JOIN account_invoice_line il ON (il.id = rel.invoice_line_id)
                  JOIN account_invoice inv ON (inv.id = il.invoice_id)
                  JOIN product_uom sol_uom ON (sol_uom.id = sol.product_uom)
                  JOIN product_uom il_uom ON (il_uom.id = il.uom_id)
                 WHERE inv.state != 'cancel'
                   AND sol_uom.category_id = il_uom.category_id
              GROUP BY sol.id
              ) as sign_qty,
               product_uom uom
         WHERE sign_qty.sol_id = l.id
           AND uom.id = l.product_uom
        """
    )

    if util.table_exists(cr, "stock_move"):
        # sale_mrp explode the BOM and check the quantity of each products (of kit).
        # Reimplementing bom exploding in sql is madness.
        # Also, as bom can change over time, we can't trust them.
        # We will just believe the stock moves...
        for table, column in [
            ("stock_move", "procurement_id"),
            ("procurement_order", "sale_line_id"),
            ("procurement_order", "state"),
        ]:
            util.create_index(cr, "%s_%s_index" % (table, column), table, column)

        cr.execute(
            """
            UPDATE sale_order_line l
               SET qty_delivered =
               round(query.sum, ceil(-log(uom.rounding))::integer)
              FROM (
                    SELECT l.id, SUM(m.product_uom_qty / mu.factor * su.factor)
                      FROM stock_move m
                      JOIN procurement_order p ON (p.id = m.procurement_id)
                      JOIN sale_order_line l ON (l.id = p.sale_line_id)
                      JOIN product_uom su ON (su.id = l.product_uom)
                      JOIN product_uom mu ON (mu.id = m.product_uom)
                      JOIN stock_location sl ON (sl.id = m.location_dest_id)
                     WHERE m.state='done'
                       AND p.state='done'
                       AND sl.usage='customer'
                       AND sl.scrap_location=false
                       AND su.category_id = mu.category_id
                  GROUP BY l.id
                  ) AS query,
                   product_uom uom
             WHERE query.id = l.id
               AND uom.id = l.product_uom
            """
        )
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

    cr.execute(
        """
        UPDATE sale_order_line l
           SET qty_to_invoice = CASE
                WHEN state NOT IN ('sale', 'done') THEN 0
                -- price_subtotal will be computed and stored by ORM later...
                WHEN (product_uom_qty * price_unit * (1 - coalesce(discount, 0) / 100)) = 0 THEN 0
                -- if the sale is done and the linked invoice is open/paid (if any),
                -- consider that there is nothing to invoice anymore
                WHEN     state = 'done'
                     AND EXISTS(SELECT 1 FROM sale_order_line_invoice_rel WHERE order_line_id = l.id)
                     AND NOT EXISTS(SELECT 1
                                      FROM sale_order_line_invoice_rel r
                                      JOIN account_invoice_line il ON (r.invoice_line_id = il.id)
                                      JOIN account_invoice i ON (il.invoice_id = i.id)
                                     WHERE r.order_line_id = l.id
                                       AND i.state NOT IN ('open', 'paid', 'cancel'))
                THEN 0
                WHEN EXISTS(SELECT 1
                              FROM product_product p
                              JOIN product_template t ON (t.id = p.product_tmpl_id)
                             WHERE p.id = l.product_id
                               AND t.invoice_policy = 'order')
                THEN GREATEST(0, round(product_uom_qty - coalesce(qty_invoiced, 0), ceil(-log(uom.rounding))::integer))
                ELSE GREATEST(0, round(qty_delivered - coalesce(qty_invoiced, 0), ceil(-log(uom.rounding))::integer))
                END
          FROM product_uom uom
         WHERE uom.id = l.product_uom
    """
    )

    # compute invoice_status field: https://git.io/v2MWu
    cr.execute(
        """
        UPDATE sale_order_line l
           SET invoice_status = CASE
                WHEN state NOT IN ('sale', 'done') THEN 'no'
                WHEN qty_to_invoice = 0 AND (product_uom_qty * price_unit * (1 - coalesce(discount, 0) / 100)) = 0 THEN 'invoiced'
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
        """.format(
            all_moves_done=all_moves_done
        )
    )

    # in 8.0, there use to be a m2m sale.order <=> account.invoice
    # Now, only the m2m sale.order.line <=> account.invoice.line is used to find the invoices
    # linked to a sale.order
    # However this m2m does not always contains the correct links
    # This will cause the field `qty_invoiced` to be NULL (undermined).
    # Try to guess if SO is fully paid by comparing invoice amounts

    cr.execute(
        """
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
               SET invoice_status = 'invoiced', qty_to_invoice = 0
              FROM sol_inv s
             WHERE s.id = l.id
               AND NOT EXISTS(
                    SELECT 1
                      FROM account_invoice
                     WHERE id = ANY(s.invoices)
                       AND (state NOT IN ('open', 'paid', 'cancel') OR currency_id != s.currency_id)
               )
               AND s.amount_total <= (SELECT SUM(amount_total)
                                        FROM account_invoice
                                       WHERE state IN ('open', 'paid')
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
                   AND state NOT IN ('open', 'paid', 'cancel')
           )
           AND EXISTS(
                SELECT 1
                  FROM account_invoice
                 WHERE id = ANY(s.invoices)
                   AND state IN ('open', 'paid')
                   AND currency_id != s.currency_id)

    """
    )
    invoiced = []
    env = util.env(cr)
    Currency = env["res.currency"]
    for sol_id, amount_total, currency_id, order_date, company_id, invoice_ids in cr.fetchall():
        cur_t = Currency.browse(currency_id).with_context(company_id=company_id, date=order_date)
        total = 0.0
        cr.execute(
            """
            SELECT amount_total, currency_id, date_invoice, company_id
              FROM account_invoice
             WHERE id IN %s
               AND state IN ('open', 'paid')
        """,
            [tuple(invoice_ids)],
        )
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
        cr.execute("UPDATE sale_order_line SET invoice_status='invoiced' WHERE id IN %s", [tuple(invoiced)])

    cr.execute("UPDATE sale_order_line SET invoice_status='to invoice' WHERE invoice_status IS NULL")

    # Link every order line with every invoice line of linked invoice
    cr.execute(
        """
        INSERT INTO sale_order_line_invoice_rel(order_line_id, invoice_line_id)
             SELECT ol.id, il.id
               FROM sale_order_line ol
               JOIN sale_order_invoice_rel r ON (r.order_id = ol.order_id)
               JOIN account_invoice_line il ON (r.invoice_id = il.invoice_id)
              WHERE NOT EXISTS(SELECT 1
                                 FROM sale_order_line_invoice_rel
                                WHERE order_line_id = ol.id)
                AND ol.invoiced = true
    """
    )

    # compute `invoice_status` of `sale_order`
    cr.execute(
        """
        WITH s AS (
            SELECT so.id,
                   CASE WHEN so.state NOT IN ('done', 'sale') THEN 'no'
                        WHEN 'to invoice' = any(array_agg(line.invoice_status)) THEN 'to invoice'
                        WHEN 'invoiced' = all(array_agg(line.invoice_status)) THEN 'invoiced'
                        WHEN array_agg(line.invoice_status)::text[] <@ ARRAY['invoiced', 'upselling'] THEN 'upselling'
                        ELSE 'no'
                   END AS state
              FROM sale_order so
               LEFT JOIN sale_order_line line ON (so.id = line.order_id)
          GROUP BY so.id
        )
        UPDATE sale_order so
           SET invoice_status = s.state
          FROM s
         WHERE s.id = so.id
    """
    )
