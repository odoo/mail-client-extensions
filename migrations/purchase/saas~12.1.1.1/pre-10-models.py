# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "purchase_order_line", "qty_received_method", "varchar")
    cr.execute("""
        UPDATE purchase_order_line pol
           SET qty_received_method='manual'
          FROM product_product pp
          JOIN product_template pt on pp.product_tmpl_id = pt.id
         WHERE pol.product_id=pp.id and pt.type in ('consu', 'service')
    """)
    util.create_column(cr, "purchase_order_line", "qty_received_manual", "float8")
    cr.execute("""
        UPDATE purchase_order_line
           SET qty_received_manual=CASE WHEN qty_received_method='manual' THEN qty_received ELSE 0 END
    """)
