# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
def migrate(cr, version):
    util.create_column(cr, 'purchase_order', 'currency_id', 'int4')

    cr.execute("""
        UPDATE purchase_order o
           SET currency_id = p.currency_id
          FROM product_pricelist p
         WHERE p.id = o.pricelist_id
    """)
