# -*- coding: utf-8 -*-
from operator import itemgetter
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'product_product', 'volume', 'float8')
    util.create_column(cr, 'product_product', 'weight', 'float8')
    cr.execute("""
        UPDATE product_product p
           SET volume=t.volume,
               weight=COALESCE(NULLIF(t.weight, 0.0), t.weight_net)
          FROM product_template t
         WHERE t.id = p.product_tmpl_id
    """)
    cr.execute("""
        UPDATE product_template t
           SET volume=0, weight=0
        WHERE (SELECT COUNT(1) FROM product_product WHERE product_tmpl_id=t.id) > 1
    """)
    util.remove_field(cr, 'product.template', 'weight_net', cascade=True)

    # update product.price.history see http://git.io/vZxdR
    columns = util.get_columns(cr, 'product_price_history', ('id', 'product_template_id'))
    h_columns = ["h." + c for c in columns]

    util.create_column(cr, 'product_price_history', 'product_id', 'int4')
    cr.execute("ALTER TABLE product_price_history ALTER COLUMN product_template_id DROP NOT NULL")

    cr.execute("""INSERT INTO product_price_history({columns}, product_id)
                    SELECT {h_columns}, p.id
                      FROM product_price_history h
                      JOIN product_product p ON (h.product_template_id = p.product_tmpl_id)
               """.format(columns=','.join(columns), h_columns=','.join(h_columns)))
    cr.execute("DELETE FROM product_price_history WHERE product_id IS NULL")
    util.remove_field(cr, 'product.price.history', 'product_template_id')

    # move property field from template to product
    cr.execute("""
        INSERT INTO ir_model_fields (model, model_id, name, field_description, ttype)
             SELECT 'product.product', (SELECT id FROM ir_model WHERE model='product.product'),
                    'standard_price', 'description will be updated by ORM later', 'float'
              WHERE NOT EXISTS (SELECT 1
                                  FROM ir_model_fields
                                 WHERE model='product.product'
                                   AND name='standard_price')
    """)        # poor-man upsert...
    cr.execute("""SELECT id
                    FROM ir_model_fields
                   WHERE model IN ('product.product', 'product.template')
                     AND name='standard_price'
                ORDER BY model
               """)
    fpid, ftid = map(itemgetter(0), cr.fetchall())

    cr.execute("""UPDATE ir_property
                     SET fields_id=%s
                   WHERE fields_id=%s
               RETURNING id, res_id
               """, [fpid, ftid])
    for prop_id, res_id in cr.fetchall():
        if not res_id:
            continue
        _, _, tid = res_id.partition(',')
        cr.execute("SELECT id FROM product_product WHERE product_tmpl_id=%s", [tid])
        pids = map(itemgetter(0), cr.fetchall())
        if not pids:
            continue
        cr.execute("UPDATE ir_property SET res_id=CONCAT('product.product,', %s) WHERE id=%s",
                   [pids[0], prop_id])
        pids.pop(0)
        if pids:
            cr.execute("""
                WITH u AS (SELECT unnest(%s) as id)
                INSERT INTO ir_property(name, type, fields_id, company_id, res_id, value_float)
                SELECT name, type, fields_id, company_id,
                       CONCAT('product.product,', u.id), value_float
                  FROM ir_property p, u
                 WHERE p.id=%s""", [pids, prop_id])
