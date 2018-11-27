# -*- coding: utf-8 -*-
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
    cr.execute("SELECT id FROM sale_order WHERE currency_rate IS NULL")
    so_ids = [r[0] for r in cr.fetchall()]
    util.recompute_fields(cr, "sale.order", ["currency_rate"], ids=so_ids, chunk_size=SZ)

    cr.execute(
        """
        SELECT r.order_line_id
          FROM sale_order_line_invoice_rel r
          JOIN account_invoice_line l ON (l.id = r.invoice_line_id)
          JOIN account_invoice i ON (i.id = l.invoice_id)
         WHERE i.state IN ('open', 'in_payment', 'paid')
      GROUP BY r.order_line_id
    """
    )
    line_ids = [r[0] for r in cr.fetchall()]
    util.recompute_fields(cr, "sale.order.line", ["untaxed_amount_invoiced"], ids=line_ids, chunk_size=SZ)

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

    # Create section lines
    # Then re-generate the sequence to ensure proper order
    cr.execute(
        """
        INSERT INTO sale_order_line
            (order_id, layout_category_id, sequence, display_type, name,
             price_unit, product_uom_qty, customer_lead
            )
            SELECT s.order_id, s.layout_category_id, min(s.sequence)-5, 'line_section', l.name,
                   0, 0, 0
            FROM sale_order_line s INNER JOIN sale_layout_category l on s.layout_category_id=l.id
            GROUP BY s.order_id, s.layout_category_id, l.name
            ORDER BY s.order_id, s.layout_category_id
    """
    )
    cr.execute(
        """
        WITH new_sequence AS (
            SELECT s.id,row_number() OVER (PARTITION BY s.order_id) as sequence
            FROM sale_order_line s INNER JOIN sale_layout_category l on s.layout_category_id=l.id
            ORDER BY s.order_id, l.sequence, l.id, COALESCE(s.sequence, 0), id
        )
        UPDATE sale_order_line
        SET sequence=new_sequence.sequence
        FROM new_sequence
        WHERE sale_order_line.id=new_sequence.id
    """
    )
