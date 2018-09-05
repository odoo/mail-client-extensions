# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'stock_picking', 'sale_id', 'int4')
    if not util.column_exists(cr, 'procurement_group', 'sale_order_id'):
       util.create_column(cr, 'procurement_group', 'sale_order_id', 'int4')

    cr.execute("""
        update procurement_group pg
           set sale_order_id= so.id
          from sale_order so
          where so.procurement_group_id=pg.id
          and so.procurement_group_id is not null
    """)

    cr.execute("""
        UPDATE stock_picking p
           SET sale_id = l.order_id
          FROM stock_move m
          JOIN procurement_order po ON (po.id = m.procurement_id)
          JOIN sale_order_line l ON (l.id = po.sale_line_id)
         WHERE m.picking_id = p.id
    """)
