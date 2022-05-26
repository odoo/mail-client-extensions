# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "purchase_order_line", "qty_to_invoice", "numeric")

    cr.execute(
        """
        UPDATE purchase_order_line pol
           SET qty_to_invoice = CASE
                    WHEN po.state in ('purchase', 'done') AND pt.purchase_method = 'purchase'
                      THEN pol.product_uom_qty - pol.qty_invoiced
                    WHEN po.state in ('purchase', 'done') AND pt.purchase_method != 'purchase'
                      THEN pol.qty_received - pol.qty_invoiced
                    ELSE 0.0
               END
          FROM purchase_order po,
               product_product p
          JOIN product_template pt ON p.product_tmpl_id = pt.id
         WHERE pol.order_id = po.id
           AND pol.product_id = p.id
        """
    )

    # recompute `invoice_status` based on new code of saas~13.3
    # XXX should we?
    cr.execute(
        """
        WITH pol_po AS (
            SELECT po.id,
                CASE
                    WHEN po.state NOT IN ('purchase', 'done') THEN 'no'
                    WHEN bool_or(l.qty_to_invoice != 0) THEN 'to invoice'
                    WHEN bool_and(l.qty_to_invoice = 0) AND
                            EXISTS(SELECT 1 FROM account_move_purchase_order_rel p_rel WHERE p_rel.purchase_order_id = po.id)
                        THEN 'invoiced'
                    ELSE 'no'
                END AS invoice_status
              FROM purchase_order po
         LEFT JOIN purchase_order_line l ON l.order_id = po.id
          GROUP BY po.id
        )
        UPDATE purchase_order po
           SET invoice_status = p.invoice_status
          FROM pol_po p
         WHERE po.id = p.id
        """
    )

    util.create_column(cr, "purchase_order", "date_calendar_start", "timestamp without time zone")
    cr.execute(
        """
        UPDATE purchase_order
        SET date_calendar_start = CASE WHEN state IN ('purchase', 'done') THEN date_approve
                                       ELSE date_order
                                  END
        """
    )

    util.create_column(cr, "purchase_order", "expected_date", "timestamp without time zone")
    cr.execute(
        """
        WITH pol AS (
                SELECT order_id, MIN(date_planned) as date_planned
                  FROM purchase_order_line
                 WHERE date_planned IS NOT NULL
              GROUP BY order_id
        )
        UPDATE purchase_order po
           SET expected_date = pol.date_planned
          FROM pol
         WHERE pol.order_id = po.id
    """
    )

    # data
    gone = """
        # filters
        filter_purchase_order_monthly_purchases
        filter_purchase_order_price_per_supplier
        filter_purchase_order_average_delivery_time

        # access
        access_product_group_res_partner_purchase_manager
        access_account_journal_purchase_manager

        # actions
        purchase_order_action_generic
    """
    for xid in util.splitlines(gone):
        util.remove_record(cr, f"purchase.{xid}")

    util.remove_menus(cr, [util.ref(cr, "purchase.menu_report_purchase")])
