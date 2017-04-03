# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'stock_picking', 'sale_id', 'int4')
    cr.execute("""
        UPDATE stock_picking p
           SET sale_id = l.order_id
          FROM stock_move m
          JOIN procurement_order po ON (po.id = m.procurement_id)
          JOIN sale_order_line l ON (l.id = po.sale_line_id)
         WHERE m.picking_id = p.id
    """)
