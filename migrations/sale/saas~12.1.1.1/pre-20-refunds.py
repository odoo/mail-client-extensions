# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_gte("saas~12.4"):
        tables_and_fields = {
            "invoice": "account_move",
            "invoice_line": "account_move_line",
            "invoice_id": "move_id",
            "refund_invoice_id": "reversed_entry_id",
            "uom_id": "product_uom_id",
            "number": "name",
            "origin": "invoice_origin",
        }
    else:
        tables_and_fields = {
            "invoice": "account_invoice",
            "invoice_line": "account_invoice_line",
            "invoice_id": "invoice_id",
            "refund_invoice_id": "refund_invoice_id",
            "uom_id": "uom_id",
            "number": "number",
            "origin": "origin",
        }

    cr.execute(
        """
        INSERT INTO sale_order_line_invoice_rel (invoice_line_id, order_line_id)
             SELECT r_id, ol_id
               FROM (SELECT ril.id AS r_id,
                            (array_agg(irel.order_line_id ORDER BY irel.order_line_id)::int[])[(
                                    SELECT array_position(array_agg(ail.id ORDER BY ail.id), ril.id)
                                      FROM {invoice_line} ail
                                     WHERE ail.{invoice_id} = ril.{invoice_id}
                                       AND ail.product_id = ril.product_id
                                       AND ail.name = ril.name
                                       AND ail.price_subtotal = ril.price_subtotal)] AS ol_id
                       FROM {invoice_line} ril
                       JOIN {invoice} r ON (ril.{invoice_id} = r.id)
                       JOIN {invoice} i ON (r.{refund_invoice_id} = i.id)
                       JOIN {invoice_line} il ON (i.id = il.{invoice_id})
                       JOIN sale_order_line_invoice_rel irel ON (irel.invoice_line_id = il.id)
                  LEFT JOIN sale_order_line_invoice_rel rrel ON (rrel.invoice_line_id = ril.id)
                      WHERE rrel.order_line_id IS NULL
                        AND il.product_id = ril.product_id
                        AND r.state IN ('open', 'paid')
                        AND il.name = ril.name
                        AND il.quantity = ril.quantity
                        AND il.{uom_id} = ril.{uom_id}
                        AND ril.price_subtotal = il.price_subtotal
                        AND ril.price_unit = il.price_unit
                   GROUP BY ril.id, r.{number}, r.{origin}, i.{number}, ril.product_id, ril.name
                   ORDER BY ril.id
                    ) x
             WHERE ol_id IS NOT NULL
    """.format(
            **tables_and_fields
        )
    )
