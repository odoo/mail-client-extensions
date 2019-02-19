# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("""
        UPDATE purchase_order_line pol
           SET qty_received_method='stock_moves'
          FROM product_product pp, product_template pt
         WHERE pol.product_id=pp.id
           AND pt.type in ('consu', 'product')
           AND pp.product_tmpl_id=pt.id
    """)
