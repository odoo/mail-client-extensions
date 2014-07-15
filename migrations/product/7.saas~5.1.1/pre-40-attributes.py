# -*- coding: utf-8 -*-
from collections import defaultdict
from openerp.addons.base.maintenance.migrations import util

def _create_tables(cr):
    if not util.table_exists(cr, 'product_attribute'):
        cr.execute("""CREATE TABLE product_attribute(
                        id SERIAL NOT NULL,
                        name varchar,
                        PRIMARY KEY(id)
                      )
                   """)

    if not util.table_exists(cr, 'product_attribute_value'):
        cr.execute("""CREATE TABLE product_attribute_value(
                        id SERIAL NOT NULL,
                        sequence int,
                        name varchar,
                        attribute_id int,
                        PRIMARY KEY(id)
                      )
                   """)
    else:
        util.create_column(cr, 'product_attribute_value', 'sequence', 'int4')

    if not util.table_exists(cr, 'product_attribute_line'):
        cr.execute("""CREATE TABLE product_attribute_line(
                        id SERIAL NOT NULL,
                        product_tmpl_id int,
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
    cr.execute("""CREATE TABLE product_attribute_value_product_product_rel(
                    att_id int, prod_id int)""")
    cr.execute("""CREATE TABLE product_attribute_line_product_attribute_value_rel(
                    line_id int, val_id int)""")


def _migrate_tables(cr):
    _create_tables(cr)

    util.create_column(cr, 'product_attribute_value', '_tmp', 'int4')
    cr.execute("""WITH newvalues AS (
                        INSERT INTO product_attribute_value(sequence, attribute_id, name, _tmp)
                             SELECT 1, l.attribute_id, l.value::text, l.id
                               FROM product_attribute_line l
                         INNER JOIN product_attribute t ON t.id = l.attribute_id
                              WHERE t.type = 'float'
                                AND l.value IS NOT NULL
                          RETURNING _tmp, id
                       )
                       INSERT INTO product_attribute_line_product_attribute_value_rel(line_id, val_id)
                            SELECT *
                              FROM newvalues
               """)
    util.remove_column(cr, 'product_attribute_value', '_tmp')

    cr.execute("""INSERT INTO product_attribute_line_product_attribute_value_rel(line_id, val_id)
                       SELECT id, value_id
                         FROM product_attribute_line
                        WHERE value_id IS NOT NULL
               """)

    # link each product with each attributes (of its template)
    cr.execute("""INSERT INTO product_attribute_value_product_product_rel(att_id, prod_id)
                       SELECT r.val_id, p.id
                         FROM product_product p
                   INNER JOIN product_attribute_line l ON p.product_tmpl_id = l.product_tmpl_id
                   INNER JOIN product_attribute_line_product_attribute_value_rel r ON r.line_id = l.id
               """)
    # remove old required columns
    util.remove_field(cr, 'product.attribute', 'type')

def migrate(cr, version):
    # create an attribute per variant to avoid it to be delete when template is edited.

    if util.table_exists(cr, 'product_attribute'):
        # in saas-{3,4}, website_sale created the table... convert content
        _migrate_tables(cr)
    else:
        _create_tables(cr)

    att_id = None
    variant2value = {}
    by_tmpl = defaultdict(set)

    class Agg(object):
        def __getitem__(self, what):
            return 'unnest(array_agg({0}))'.format(what)

    cr.execute("""SELECT product_tmpl_id,
                         {agg[id]}, {agg[price_extra]},
                         {agg[coalesce(variants, default_code, '/')]}
                    FROM product_product
                GROUP BY product_tmpl_id
                  HAVING count(id) > 1
               """.format(agg=Agg()))

    for tmpl_id, prod_id, price, variant in cr.fetchall():
        by_tmpl[tmpl_id].add((prod_id, price, variant))

    for tmpl_id, attrs in by_tmpl.items():
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

            if variant not in variant2value:
                cr.execute("""INSERT INTO product_attribute_value(sequence, name, attribute_id)
                                   VALUES (1, %s, %s)
                                RETURNING id
                           """, (variant, att_id))
                [variant2value[variant]] = cr.fetchone()

            value_id = variant2value[variant]

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
