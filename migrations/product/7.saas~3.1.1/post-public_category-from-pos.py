# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # in saas-3, the model pos.category has been renamed to product.public.category and promoted
    # to product module
    # but it's back in saas-5.
    if version and not version.startswith(('7.saas~3', '7.saas~4')):
        return
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
