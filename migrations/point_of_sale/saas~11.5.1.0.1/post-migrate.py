# -*- coding: utf-8 -*-
from operator import itemgetter
from odoo.addons.base.maintenance.migrations import util
import logging
import os


def migrate(cr, version):
    env = util.env(cr)
    _logger = logging.getLogger(__name__)
    env_variable = 'ODOO_MIG_12_POS_MIGRATION_SQL'
    if os.environ.get(env_variable):
        cr.execute("""
                    WITH lines as (SELECT o.pricelist_id,o.fiscal_position_id, l.product_id, l.qty,array_agg(DISTINCT t.account_tax_id) as tax_ids,l.id, l.discount, l.price_unit
                    from pos_order_line l
                    left join pos_order o on o.id=l.id
                    LEFT JOIN account_tax_pos_order_line_rel t on l.id=t.pos_order_line_id
                    GROUP BY 1,2,3,4,6,7, 8)
                    SELECT pricelist_id,fiscal_position_id,product_id,price_unit, qty,tax_ids,discount,array_agg(id) agg
                    FROM lines
                    group by 1,2,3,4,5,6,7
        """)
        for row in cr.fetchall():
            ids = row[7] # column 8 in SQL is 7 in Python :-)
            orderlines = env["pos.order.line"].browse([ids[0], ])
            res = orderlines[0]._compute_amount_line_all()
            cr.execute("""
                UPDATE pos_order_line
                SET price_subtotal_incl=%s,
                    price_subtotal=%s
                WHERE id=ANY(%s) 
            """, [res['price_subtotal_incl'], res['price_subtotal'], list(ids)])

        cr.execute("""
            WITH paid as (
                SELECT pos_statement_id, sum(amount) as paid
                FROM account_bank_statement_line
                group by pos_statement_id
            )
            UPDATE pos_order o
            SET amount_paid=paid.paid
            FROM paid
            WHERE o.id=paid.pos_statement_id
        """)
        cr.execute("""
            WITH paid as (
                SELECT pos_statement_id, sum(amount) as paid
                FROM account_bank_statement_line
                WHERE amount<0
                group by pos_statement_id
            )
            UPDATE pos_order o
            SET amount_return=paid.paid
            FROM paid
            WHERE o.id=paid.pos_statement_id
        """)
        cr.execute("""
            WITH amount as (
                SELECT order_id, sum(price_subtotal_incl) as incl, sum(coalesce(price_subtotal_incl,0)-coalesce(price_subtotal,0)) as taxes
                FROM pos_order_line
                group by order_id
            )
            UPDATE pos_order o
            SET amount_tax=amount.taxes,
                amount_total=amount.incl
            FROM amount
            WHERE o.id=amount.order_id
        """)

        cr.execute(""" update pos_order set amount_paid = 0 where amount_paid is NULL""")
        cr.execute(""" update pos_order set amount_return = 0 where amount_return is NULL""")

    else:
        # standard pos migration
        cr.execute("SELECT count(*) cnt FROM pos_order_line")
        pol_count= cr.fetchone()[0]
        if pol_count > 300000:
            _logger.warning("""there are %s pos order lines, this is considered as a big amount,
                maybe you should consider to set the following environement variable %s : """ % (pol_count, env_variable))

        cr.execute("SELECT id FROM pos_order_line")
        ids = list(map(itemgetter(0), cr.fetchall()))
        orderlines = util.iter_browse(env["pos.order.line"], ids)
        for orderline in orderlines:
            orderline._onchange_amount_line_all()

        cr.execute("SELECT id FROM pos_order")
        ids = list(map(itemgetter(0), cr.fetchall()))
        orders = util.iter_browse(env["pos.order"], ids)
        for order in orders:
            order._onchange_amount_all()
