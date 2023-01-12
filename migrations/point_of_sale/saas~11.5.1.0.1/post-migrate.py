# -*- coding: utf-8 -*-
from operator import itemgetter
from odoo.addons.base.maintenance.migrations import util
from odoo.sql_db import connection_info_for
import logging
import psycopg2
import os

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = util.env(cr)
    env_big_pos = 'ODOO_MIG_12_POS_MIGRATION_SQL'
    if not os.environ.get(env_big_pos):
        # standard pos migration
        cr.execute("SELECT id FROM pos_order_line")
        if cr.rowcount > 300000:
            _logger.warning("""There are %s pos order lines, this is considered as a big amount,
                maybe you should consider to set the following environement variable %s : """ % (cr.rowcount, env_big_pos))
        ids = list(map(itemgetter(0), cr.fetchall()))
        orderlines = util.iter_browse(env["pos.order.line"], ids)
        for orderline in orderlines:
            orderline._onchange_amount_line_all()

        cr.execute("SELECT id FROM pos_order")
        ids = list(map(itemgetter(0), cr.fetchall()))
        orders = util.iter_browse(env["pos.order"], ids)
        for order in orders:
            order._onchange_amount_all()
    else:
        # Alternate flow for pos processing
        # We categorize all pos lines based on params that can affect the price computation (fpox, taxes, etc.)
        # We store that categorization in a temporary table
        # We process one line from each category and compute its price, then push the result to all line of the same category
        # Since the amount of lines can be ginormous, we use a server-side cursor to avoid a MemoryError
        _logger.info('creating temporary table')
        # Store the categorization, all columns are important params that impact the computation except
        # the last one which contains the matching lines as an array
        cr.execute("""CREATE TABLE mig_temp_post_order_compute (line_ids integer[])""")
        cr.execute("""
            WITH lines as (
                    SELECT o.pricelist_id,
                            o.fiscal_position_id,
                            l.product_id,
                            l.qty,
                            array_agg(DISTINCT t.account_tax_id ORDER BY t.account_tax_id) as tax_ids,
                            l.id,
                            l.discount,
                            l.price_unit
                    FROM pos_order_line l
                    JOIN pos_order o ON o.id=l.order_id
                    LEFT JOIN account_tax_pos_order_line_rel t ON l.id=t.pos_order_line_id
                    GROUP BY 1,2,3,4,6,7,8
                )
       INSERT INTO mig_temp_post_order_compute (line_ids)
            SELECT array_agg(id) agg
              FROM lines
          GROUP BY pricelist_id,
                   fiscal_position_id,
                   product_id,
                   price_unit,
                   qty,
                   tax_ids,
                   discount
        """)
        def compute_for_group(ids):
            # process a category of lines: compute amounts based on first line of group, then push the result via postgres
            orderlines = env["pos.order.line"].browse([ids[0], ])
            res = orderlines[0]._compute_amount_line_all()
            cr.execute("""
                UPDATE pos_order_line
                   SET price_subtotal_incl=%s,
                       price_subtotal=%s
                 WHERE pos_order_line.id IN %s
            """, [res['price_subtotal_incl'], res['price_subtotal'], tuple(ids)])

        # We need to make sure that the cursor we're about to open has the temp table available to it
        cr.commit()
        # Open an alternate cursor that will remain postgres-side instead of trying to load everything in memory
        db, conn_info = connection_info_for(cr.dbname)
        with psycopg2.connect(**conn_info) as conn:
            with conn.cursor(name='hyuge_pos') as alt_cr:
                done = 0
                cr.execute("SELECT count(*) FROM mig_temp_post_order_compute")
                total_groups = cr.fetchone()[0]
                ROWS_TO_FETCH = 10**5
                alt_cr.execute("""
                    SELECT line_ids
                    FROM mig_temp_post_order_compute
                """)
                rows = alt_cr.fetchmany(ROWS_TO_FETCH)
                while rows:
                    _logger.info('Computing total for order line groups (%s/%s)', done + len(rows), total_groups)
                    for ids, in rows:
                        compute_for_group(ids)
                    env['pos.order.line'].invalidate_cache()
                    rows = alt_cr.fetchmany(ROWS_TO_FETCH)
                    done += len(rows)

        cr.execute(""" DROP TABLE mig_temp_post_order_compute """)  # clean up that shit
        # Now let's process the orders
        util.parallel_execute(cr, util.explode_query_range(cr, """
            WITH payments AS (
                    SELECT l.pos_statement_id, SUM(l.amount) as paid, SUM(CASE WHEN l.amount < 0 THEN l.amount END) as returned
                      FROM account_bank_statement_line l
                      JOIN pos_order o ON o.id = l.pos_statement_id
                     WHERE {parallel_filter}
                     GROUP BY l.pos_statement_id
                )
            UPDATE pos_order o
            SET amount_paid = payments.paid,
                amount_return = COALESCE(payments.returned, 0)
            FROM payments
            WHERE o.id=payments.pos_statement_id
        """, table="pos_order", alias="o"))
        util.parallel_execute(cr, util.explode_query_range(cr, """
            WITH amount as (
                SELECT l.order_id, sum(l.price_subtotal_incl) as incl, sum(coalesce(l.price_subtotal_incl,0)-coalesce(l.price_subtotal,0)) as taxes
                  FROM pos_order_line l
                  JOIN pos_order o ON o.id = l.order_id
                 WHERE {parallel_filter}
                 GROUP BY l.order_id
            )
            UPDATE pos_order o
            SET amount_tax=amount.taxes,
                amount_total=amount.incl
            FROM amount
            WHERE o.id=amount.order_id
        """, table="pos_order", alias="o"))
        # Clean up, ensure value since this is a required field
        util.parallel_execute(cr, util.explode_query_range(cr, """
            UPDATE pos_order
            SET amount_paid=COALESCE(amount_paid, 0),
                amount_return=COALESCE(amount_return, 0),
                amount_tax=COALESCE(amount_tax, 0),
                amount_total=COALESCE(amount_total, 0)
            WHERE (amount_paid IS NULL
               OR amount_return IS NULL
               OR amount_tax IS NULL
               OR amount_total IS NULL)
               AND {parallel_filter}
        """, table="pos_order"))
