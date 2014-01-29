# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""UPDATE product_template
                     SET image = p.image,
                         image_medium = p.image_medium,
                         image_small = p.image_small
                    FROM product_product p
                   WHERE p.product_template_id = id
                """)

    util.remove_field(cr, 'product.product', 'image')
    util.remove_field(cr, 'product.product', 'image_medium')
    util.remove_field(cr, 'product.product', 'image_small')
