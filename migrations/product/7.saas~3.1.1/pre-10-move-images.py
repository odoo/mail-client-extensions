# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
from openerp.release import serie as series

def migrate(cr, version):
    util.create_column(cr, 'product_template', 'image', 'bytea')
    util.create_column(cr, 'product_template', 'image_medium', 'bytea')
    util.create_column(cr, 'product_template', 'image_small', 'bytea')

    if series != '7.saas~3':
        util.create_column(cr, 'product_product', 'image_variant', 'bytea')
        cr.execute("""UPDATE product_product
                         SET image_variant = image
                         where product_tmpl_id in (select product_tmpl_id from product_product group by product_tmpl_id having count(id)>1)""")

    cr.execute("""UPDATE product_template
                     SET image = p.image,
                         image_medium = p.image_medium,
                         image_small = p.image_small
                    FROM product_product p
                   WHERE p.product_tmpl_id = product_template.id
                """)

