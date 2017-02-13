# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'ir_attachment', 'product_downloadable', 'boolean')
    cr.execute("""
        WITH products AS (
            SELECT 'product.template' as model, id
              FROM product_template
             WHERE type = 'digital'
             UNION
            SELECT 'product.product' as model, p.id
              FROM product_product p
              JOIN product_template t ON (t.id = p.product_tmpl_id)
             WHERE t.type = 'digital'
        )
        UPDATE ir_attachment a
           SET product_downloadable=true
          FROM products p
         WHERE a.res_model = p.model
           AND a.res_id = p.id
    """)

    cr.execute("UPDATE product_template SET type='service' WHERE type='digital'")
