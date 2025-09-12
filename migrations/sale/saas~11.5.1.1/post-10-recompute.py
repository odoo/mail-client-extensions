from odoo.addons.base.maintenance.migrations import util

SZ = 1024


def migrate(cr, version):
    cr.execute(
        """
        UPDATE sale_order o
           SET currency_rate = 1
          FROM res_company c,
               product_pricelist p
         WHERE c.id = o.company_id
           AND p.id = o.pricelist_id
           AND c.currency_id = p.currency_id
    """
    )
    query = "SELECT id FROM sale_order WHERE currency_rate IS NULL AND company_id IS NOT NULL"
    util.recompute_fields(cr, "sale.order", ["currency_rate"], query=query, chunk_size=SZ)

    # some database does not contain company id value on sale order as not required field
    cr.execute("UPDATE sale_order SET currency_rate = 1 WHERE currency_rate IS NULL")

    # To compute the currency, sale order lines need to have a related company_id, which we will set to
    # the company_id from the related sale_order, but in case there are sale_order records with no
    # company_id, we set a default one
    cr.execute(
        """
        UPDATE sale_order s
           SET company_id=COALESCE(p.company_id, u.company_id)
          FROM res_users u, res_partner p
         WHERE COALESCE(s.user_id, s.create_uid)=u.id
           AND s.partner_id=p.id
           AND s.company_id IS NULL
        """
    )

    # for some reason, some related fields from the past might not be set correctly
    # (3 databases so far had the problem), so we make sure the company_id field is
    # correctly set on sale and invoice lines otherwise the currency computation crashes
    cr.execute(
        """
        UPDATE sale_order_line  sol
            SET company_id=so.company_id
            FROM sale_order so
            WHERE so.id=sol.order_id AND
                  sol.company_id IS NULL
        """
    )
    # when the currency of a sale order line is the same of all its associated invoice lines
    # we can than compute with the stored amounts since no currency rate is needed
    # https://github.com/odoo/odoo/blob/ffca224ebe3731ffdff2f18fd0b340f904ff4187/addons/sale/models/sale.py#L1370-L1372
    # we can match currencies whe at least one of the currencies is not null
    # https://github.com/odoo/odoo/blob/ffca224ebe3731ffdff2f18fd0b340f904ff4187/odoo/addons/base/models/res_currency.py#L197-L204
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
            WITH vals AS (
                SELECT sl.id,
                       sum(
                            CASE WHEN i.type='out_invoice' THEN  round(il.price_subtotal,c.decimal_places)
                                 WHEN i.type='out_refund'  THEN -round(il.price_subtotal,c.decimal_places)
                                 ElSE 0
                            END
                       ) AS untaxed_amount_invoiced
                  FROM sale_order_line_invoice_rel r
                  JOIN account_invoice_line il
                    ON il.id = r.invoice_line_id
                  JOIN account_invoice i
                    ON i.id = il.invoice_id
                  JOIN sale_order_line sl
                    ON sl.id = r.order_line_id
                  JOIN res_currency c
                    ON sl.currency_id=c.id
                 WHERE i.state IN ('open', 'in_payment', 'paid')
                   AND {parallel_filter}
                 GROUP BY sl.id
                    -- we want all invoice lines to have either NULL or same currency as the order line
                HAVING bool_and(COALESCE(il.currency_id, sl.currency_id)=sl.currency_id)
            ) UPDATE sale_order_line sl
                 SET untaxed_amount_invoiced=v.untaxed_amount_invoiced
                FROM vals v
               WHERE sl.id=v.id
            """,
            table="sale_order_line",
            alias="sl",
        ),
    )
    # collect the sale order lines not updated above
    query = """
        SELECT sl.id
          FROM sale_order_line_invoice_rel r
          JOIN account_invoice_line il
            ON il.id = r.invoice_line_id
          JOIN account_invoice i
            ON i.id = il.invoice_id
          JOIN sale_order_line sl
            ON sl.id = r.order_line_id
         WHERE i.state IN ('open', 'in_payment', 'paid')
           AND sl.untaxed_amount_invoiced IS NULL
         GROUP BY sl.id
        """
    util.recompute_fields(cr, "sale.order.line", ["untaxed_amount_invoiced"], query=query, chunk_size=SZ)

    cr.execute(
        """
        UPDATE sale_order_line l
           SET untaxed_amount_to_invoice = CASE WHEN t.invoice_policy = 'delivery'
                                                THEN l.price_reduce * l.qty_delivered
                                                ELSE l.price_reduce * l.product_uom_qty
                                            END - COALESCE(untaxed_amount_invoiced, 0)
          FROM product_product p
          JOIN product_template t ON (t.id = p.product_tmpl_id)
         WHERE p.id = l.product_id
           AND l.state IN ('sale', 'done')
    """
    )

    # Create section lines for sale_order_lines
    # Then re-generate the sequence to ensure proper order
    cr.execute(
        """
        INSERT INTO sale_order_line
            (order_id, layout_category_id, sequence, display_type, name,
             price_unit, product_uom_qty, customer_lead, company_id, currency_id
            )
            SELECT s.order_id, s.layout_category_id, min(s.sequence)-5, 'line_section', l.name,
                   0, 0, 0, s.company_id, s.currency_id
            FROM sale_order_line s INNER JOIN sale_layout_category l on s.layout_category_id=l.id
            GROUP BY s.order_id, s.layout_category_id, l.name, s.company_id, s.currency_id
            ORDER BY s.order_id, s.layout_category_id
    """
    )
    cr.execute(
        """
        WITH new_sequence AS (
            SELECT s.id,row_number() OVER (
                PARTITION BY s.order_id
                ORDER BY s.order_id, l.sequence, l.id, COALESCE(s.sequence, 0), s.id
            ) as sequence
            FROM sale_order_line s INNER JOIN sale_layout_category l on s.layout_category_id=l.id
        )
        UPDATE sale_order_line
        SET sequence=new_sequence.sequence
        FROM new_sequence
        WHERE sale_order_line.id=new_sequence.id
    """
    )

    # same thing for account_invoice_line
    cr.execute(
        """
        INSERT INTO account_invoice_line
            (invoice_id, layout_category_id, sequence, display_type, name,
             price_unit, quantity
            )
            SELECT il.invoice_id, il.layout_category_id, min(il.sequence)-5, 'line_section', l.name,
                   0, 0
            FROM account_invoice_line il INNER JOIN sale_layout_category l on il.layout_category_id=l.id
            GROUP BY il.invoice_id, il.layout_category_id, l.name
            ORDER BY il.invoice_id, il.layout_category_id
    """
    )
    cr.execute(
        """
        WITH new_sequence AS (
            SELECT il.id,row_number() OVER (
                PARTITION BY il.invoice_id
                ORDER BY il.invoice_id, l.sequence, l.id, COALESCE(il.sequence, 0), il.id
            ) as sequence
            FROM account_invoice_line il INNER JOIN sale_layout_category l on il.layout_category_id=l.id
        )
        UPDATE account_invoice_line
        SET sequence=new_sequence.sequence
        FROM new_sequence
        WHERE account_invoice_line.id=new_sequence.id
    """
    )
