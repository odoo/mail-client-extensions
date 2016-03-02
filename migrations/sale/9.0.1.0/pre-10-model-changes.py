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
    util.create_column(cr, 'sale_order_line', 'qty_invoiced', 'float8')
    util.create_column(cr, 'sale_order_line', 'qty_to_invoice', 'float8')
    util.create_column(cr, 'sale_order_line', 'qty_delivered', 'float8')
    util.create_column(cr, 'sale_order_line', 'currency_id', 'int4')
    util.create_column(cr, 'product_template', 'invoice_policy', 'varchar')

    cr.execute("""
        UPDATE sale_order_line
            SET qty_invoiced = sign_qty.qty
                FROM (SELECT sol.id as sol_id,SUM(il.quantity*(CASE WHEN inv.type='out_invoice' THEN 1 ELSE -1 END)) AS qty
                    FROM sale_order_line AS sol,
                         sale_order_line_invoice_rel as rel,
                         account_invoice_line as il,
                         account_invoice as inv
                    WHERE sol.id=rel.order_line_id
                        AND il.id=rel.invoice_line_id
                        AND inv.id=il.invoice_id
                        AND inv.state != 'cancel'
                    GROUP BY sol.id) as sign_qty
            WHERE sign_qty.sol_id=id
        """)
    cr.execute("""
        UPDATE sale_order_line l
           SET qty_to_invoice = CASE
                    WHEN qty_invoiced IS NOT NULL THEN product_uom_qty - qty_invoiced
                    ELSE product_uom_qty
                    END,
               currency_id=p.currency_id
          FROM sale_order o
          JOIN product_pricelist p ON (p.id = o.pricelist_id)
         WHERE o.id = l.order_id
    """)

    if util.table_exists(cr, 'stock_move'):
        cr.execute("""
            UPDATE sale_order_line SET
                qty_delivered = query.sum
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
                    GROUP BY sol.id) AS query
                WHERE query.id = sale_order_line.id;
            """)
    else:
        cr.execute("UPDATE sale_order_line SET qty_delivered=0")

    env = util.env(cr)
    order_policy = env['ir.values'].get_default('sale.order', 'order_policy')
    cr.execute("""
        UPDATE product_template
           SET invoice_policy = CASE
                WHEN %s = 'picking' AND type IN ('product', 'consu') THEN 'delivery'
                ELSE 'order'
                END
    """, [order_policy])

    # compute invoice_status field: https://git.io/v2MWu
    # XXX maybe we should let the ORM compute it itself
    cr.execute("""
        UPDATE sale_order_line l
           SET invoice_status = CASE
                WHEN state NOT IN ('sale', 'done') THEN 'no'
                WHEN qty_to_invoice != 0 THEN 'to invoice'
                WHEN (    state = 'sale'
                      AND EXISTS(SELECT 1
                                   FROM product_product p
                                   JOIN product_template t ON (t.id = p.product_tmpl_id)
                                  WHERE p.id = l.product_id
                                    AND t.invoice_policy = 'order')
                      AND qty_delivered > product_uom_qty) THEN 'upselling'
                WHEN qty_invoiced >= product_uom_qty THEN 'invoiced'
                ELSE 'no'
                END
        """)
