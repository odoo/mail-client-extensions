# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
        UPDATE product_template t
           SET description_sale = c.website_description
          FROM product_product p, delivery_carrier c
         WHERE p.product_tmpl_id = t.id
           AND c.product_id = p.id
           AND t.description_sale IS NULL
           AND c.website_description IS NOT NULL
    """)
    util.remove_column(cr, 'delivery_carrier', 'website_description')
