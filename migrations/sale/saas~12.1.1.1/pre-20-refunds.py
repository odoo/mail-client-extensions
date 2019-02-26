# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        INSERT INTO sale_order_line_invoice_rel (invoice_line_id, order_line_id)
             SELECT r_id, ol_id
               FROM (SELECT ril.id AS r_id,
                            (array_agg(irel.order_line_id ORDER BY irel.order_line_id)::int[])[(
                                    SELECT array_position(array_agg(ail.id ORDER BY ail.id), ril.id)
                                      FROM account_invoice_line ail
                                     WHERE ail.invoice_id = ril.invoice_id
                                       AND ail.product_id = ril.product_id
                                       AND ail.name = ril.name
                                       AND ail.price_subtotal = ril.price_subtotal)] AS ol_id
                       FROM account_invoice_line ril
                       JOIN account_invoice r ON (ril.invoice_id = r.id)
                       JOIN account_invoice i ON (r.refund_invoice_id = i.id)
                       JOIN account_invoice_line il ON (i.id = il.invoice_id)
                       JOIN sale_order_line_invoice_rel irel ON (irel.invoice_line_id = il.id)
                  LEFT JOIN sale_order_line_invoice_rel rrel ON (rrel.invoice_line_id = ril.id)
                      WHERE rrel.order_line_id IS NULL
                        AND il.product_id = ril.product_id
                        AND r.state IN ('open', 'paid')
                        AND il.name = ril.name
                        AND il.quantity = ril.quantity
                        AND il.uom_id = ril.uom_id
                        AND ril.price_subtotal = il.price_subtotal
                        AND ril.price_unit = il.price_unit
                   GROUP BY ril.id, r.number, r.origin, i.number, ril.product_id, ril.name
                   ORDER BY ril.id
                    ) x
             WHERE ol_id IS NOT NULL

    """
    )
