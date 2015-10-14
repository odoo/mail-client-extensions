# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'product_pricelist', 'discount_policy', 'varchar')
    cr.execute("""
        UPDATE product_pricelist
           SET discount_policy=CASE WHEN visible_discount THEN 'without_discount'
                                    ELSE 'with_discount'
                                END
    """)
