# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if not util.table_exists(cr, 'product_public_category') \
       or if util.table_exists(cr, 'product_public_category_product_template_rel'):
        return  # nothing to migrate from

    util.move_model(cr, 'product.public.categ', 'product', 'website_sale')
    # convert field m2o => m2m
    cr.execute("""CREATE TABLE product_public_category_product_template_rel(
                    product_template_id int,
                    product_public_category_id int
                  )
               """)
    cr.execute("""INSERT INTO product_public_category_product_template_rel(
                                                product_template_id, product_public_category_id)
                       SELECT id, public_categ_id
                         FROM product_template
               """)
    # note: do not remove field public_categ_id, `point_of_sale` migration script will need it
    # util.remove_field(cr, 'product.template', 'public_categ_id')
