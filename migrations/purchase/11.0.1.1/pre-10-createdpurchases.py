# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # As procurements are deleted, we need to know which stock moves created po lines with an extra field
    util.create_column(cr, 'stock_move', 'created_purchase_line_id', 'int4')
    cr.execute("""
        UPDATE stock_move m SET created_purchase_line_id = proc.purchase_line_id
        FROM procurement_order proc 
        WHERE proc.purchase_line_id IS NOT NULL AND proc.move_dest_id = m.id 
    """)
    # As procurements are deleted, we need to know which orderpoints created po lines with an extra field
    util.create_column(cr, 'purchase_order_line', 'orderpoint_id', 'int4')
    cr.execute("""
            UPDATE purchase_order_line pol SET orderpoint_id = p.orderpoint_id
            FROM procurement_order p 
            WHERE p.orderpoint_id IS NOT NULL AND p.purchase_line_id = pol.id
    """)