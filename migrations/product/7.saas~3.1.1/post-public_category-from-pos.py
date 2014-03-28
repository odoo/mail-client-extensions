# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # in saas-3, the model pos.category has been renamed to product.public.category and promoted
    # to product module
    if util.column_exists(cr, 'product_product', 'pos_categ_id'):
        cr.execute("""UPDATE product_template t
                         SET public_categ_id = (SELECT pos_categ_id
                                                  FROM product_product
                                                 WHERE product_tmpl_id = t.id
                                              ORDER BY id
                                                 LIMIT 1
                                               )
                       WHERE public_categ_id IS NULL
                   """)
