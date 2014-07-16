# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if not util.table_exists(cr, 'product_public_category'):
        return  # nothing to migrate from

    cr.execute("""SELECT id
                    FROM ir_module_module
                   WHERE name=%s
                     AND state IN %s
               """, ('website_sale', util._INSTALLED_MODULE_STATES))
    if not cr.fetchone():
        # website_sale is not installed
        # steal the model
        util.rename_model(cr, 'product.public.category', 'pos.category')
        util.move_model(cr, 'pos.category', 'product', 'point_of_sale')
        util.rename_field(cr, 'product.template', 'public_categ_id', 'pos_categ_id')
    else:
        # copy values
        cr.execute("""CREATE TABLE pos_category(
                        id SERIAL NOT NULL,
                        name varchar,
                        parent_id int,
                        sequence int,
                        image bytea,
                        image_medium bytea,
                        image_small bytea,
                        PRIMARY KEY(id)
                   """)
        cr.execute("""INSERT INTO pos_category(id, name, parent_id, sequence,
                                               image, image_medium, image_small)
                           SELECT id, name, parent_id, sequence,
                                  image, image_medium, image_small
                             FROM product_public_category
                   """)
        cr.execute("setval('pos_category_id_seq', (SELECT MAX(id) FROM pos_category))")

        util.create_column(cr, 'product_template', 'pos_categ_id', 'int4')
        cr.execute("UPDATE product_template SET pos_categ_id = public_categ_id")
