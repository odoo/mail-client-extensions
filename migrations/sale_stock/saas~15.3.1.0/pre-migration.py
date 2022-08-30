# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sale_order", "delivery_status", "varchar")
    cr.execute("""
        WITH states AS (
            SELECT sale_id AS order_id,
                   array_agg(state) as states
              FROM stock_picking
          GROUP BY 1
        )
        UPDATE sale_order so
           SET delivery_status='full'
          FROM states s
         WHERE s.order_id=so.id
           AND ARRAY['done', 'cancel']::varchar[] @> s.states
           AND array_position(s.states, 'done') > 0
    """)
    cr.execute("""
        WITH picks AS (
            SELECT distinct sale_id AS order_id
              FROM stock_picking
             WHERE state='done'
        )
        UPDATE sale_order so
           SET delivery_status='partial'
          FROM picks p
         WHERE so.id=p.order_id
           AND so.delivery_status IS NULL
    """)
    cr.execute("""
        WITH sps AS(
            SELECT sale_id AS order_id,
                   state
              FROM stock_picking
          GROUP BY 1,2
        ),
        states AS (
            SELECT order_id,
                   array_agg(state) as states
              FROM sps
          GROUP BY 1
        ),
        not_cancelled AS (
            SELECT order_id
              FROM states s
             WHERE NOT (array_position(s.states, 'cancel') > 0
                          AND 
                        array_length(s.states, 1) = 1)
        )
        UPDATE sale_order so
           SET delivery_status='pending'
          FROM not_cancelled c
         WHERE c.order_id=so.id
           AND so.delivery_status IS NULL
    """)
