# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if not util.table_exists(cr, 'product_public_category') \
       or util.table_exists(cr, 'product_public_category_product_template_rel'):
        return  # nothing to migrate from

    # we can't move_data because the demo data of website_sale
    # creates xmlids that belongs to product module
    util.move_model(cr, 'product.public.categ', 'product', 'website_sale', move_data=False)
    # rename the only one imd directly
    util.rename_xmlid(cr, 'product.categ_others', 'website_sale.categ_others')

    # convert field m2o => m2m
    util.create_m2m(cr, 'product_public_category_product_template_rel',
                    'product_template', 'product_public_category')

    cr.execute("""INSERT INTO product_public_category_product_template_rel(
                                                product_template_id, product_public_category_id)
                       SELECT id, public_categ_id
                         FROM product_template
               """)
    # note: do not remove field public_categ_id, `point_of_sale` migration script will need it
    # util.remove_field(cr, 'product.template', 'public_categ_id')
