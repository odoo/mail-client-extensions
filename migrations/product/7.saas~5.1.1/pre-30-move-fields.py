# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.convert_field_to_property(cr, 'product.template', 'standard_price', 'float',
                                   default_value=0)

    util.create_column(cr, "product_template", "active", "boolean")
    util.create_column(cr, "product_template", "color", "int4")

    cr.execute("UPDATE product_template SET active='t', color=0")

    cr.execute("""UPDATE product_template t
                     SET active=p.active,
                         color=p.color
                    FROM (SELECT product_tmpl_id,
                                 MAX(active::int)::boolean as active,
                                 MIN(color) as color
                            FROM product_product
                        GROUP BY product_tmpl_id
                    ) AS p
                   WHERE p.product_tmpl_id = t.id
               """)

    # create an attribute per variant to avoid it to be delete when template is edited.
    cr.execute("""CREATE TABLE product_attribute(
                    id SERIAL NOT NULL,
                    name varchar,
                    PRIMARY KEY(id)
                  )
               """)
    cr.execute("""CREATE TABLE product_attribute_value(
                    id SERIAL NOT NULL,
                    sequence int,
                    name varchar,
                    attribute_id int,
                    PRIMARY KEY(id)
                  )
               """)
    cr.execute("""CREATE TABLE product_attribute_price(
                    id SERIAL NOT NULL,
                    product_tmpl_id int,
                    value_id int,
                    price_extra float8,
                    PRIMARY KEY(id)
                  )
               """)
    cr.execute("""CREATE TABLE product_attribute_line(
                    id SERIAL NOT NULL,
                    product_tmpl_id int,
                    attribute_id int,
                    PRIMARY KEY(id)
                  )
               """)
    cr.execute("""CREATE TABLE product_attribute_value_product_product_rel(
                    att_id int, prod_id int)""")
    cr.execute("""CREATE TABLE product_attribute_line_product_attribute_value_rel(
                    line_id int, val_id int)""")

    att_id = None
    variants = {}
    cr.execute("""SELECT product_tmpl_id, array_agg((id, price_extra, variants))
                    FROM product_product
                GROUP BY product_tmpl_id
                  HAVING count(id) > 1
               """)
    # XXX I'm pretty sure it will fail. I will handle it if a database is in this case.
    for tmpl_id, attrs in cr.fetchall():
        if att_id is None:
            cr.execute("INSERT INTO product_attribute(name) VALUES(%s) RETURNING id",
                       ('Variant',))
            [att_id] = cr.fetchone()

        cr.execute("""INSERT INTO product_attribute_line(product_tmpl_id, attribute_id)
                           VALUES (%s, %s)
                        RETURNING id
                   """, (tmpl_id, att_id))
        [line_id] = cr.fetchone()

        for (product_id, price, variant) in attrs:
            if not variant:
                variant = "/"   # wtf?

            if variant not in variants:
                cr.execute("""INSERT INTO product_attribute_value(sequence, name, attribute_id)
                                   VALUES (1, %s, %s)
                                RETURNING id
                           """, (variant, att_id))
                [variants[variant]] = cr.fetchone()

            value_id = variants[variant]

            if price:
                cr.execute("""INSERT INTO product_attribute_price(product_tmpl_id, value_id, price_extra)
                                   VALUES (%s, %s, %s)
                           """, (tmpl_id, value_id, price))

            cr.execute("""INSERT INTO product_attribute_value_product_product_rel(att_id, prod_id)
                               VALUES (%s, %s)
                       """, (value_id, product_id))
            cr.execute("""INSERT INTO product_attribute_line_product_attribute_value_rel(line_id, val_id)
                                VALUES (%s, %s)
                       """, (line_id, value_id))
