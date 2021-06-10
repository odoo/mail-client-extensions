# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.drop_depending_views(cr, "product_attribute", "create_variant")
    cr.execute("""
        ALTER TABLE product_attribute
        ALTER COLUMN create_variant
         TYPE varchar
        USING CASE WHEN create_variant=true THEN 'always' ELSE 'no_variant' END
    """)

    util.rename_model(cr, "product.attribute.line", "product.template.attribute.line")

    cr.execute("""
        CREATE TABLE product_template_attribute_value (
            id SERIAL PRIMARY KEY,
            create_uid integer,
            create_date timestamp without time zone,
            write_uid integer,
            write_date timestamp without time zone,
            product_attribute_value_id integer,
            product_tmpl_id integer,
            price_extra float8
        )
    """)
    cr.execute("""
        INSERT INTO product_template_attribute_value(product_attribute_value_id, product_tmpl_id, price_extra)
             SELECT r.product_attribute_value_id, p.product_tmpl_id, COALESCE(i.price_extra, 0) price_extra
               FROM product_attribute_value_product_product_rel r
               JOIN product_product p
                 ON p.id = r.product_product_id
          LEFT JOIN product_attribute_price i
                 ON i.value_id = r.product_attribute_value_id AND i.product_tmpl_id = p.product_tmpl_id
           GROUP BY r.product_attribute_value_id, p.product_tmpl_id, COALESCE(i.price_extra, 0)
              UNION
             SELECT r.product_attribute_value_id, pal.product_tmpl_id, 0 as price_extra
               FROM product_attribute_line_product_attribute_value_rel r
               JOIN product_template_attribute_line pal
                 ON r.product_attribute_line_id=pal.id
               JOIN product_attribute pa
                 ON pal.attribute_id=pa.id
              WHERE pa.create_variant='no_variant'
    """)
    cr.execute("""
        ALTER TABLE product_attribute_line_product_attribute_value_rel
          RENAME TO product_attribute_value_product_template_attribute_line_rel
    """)
    cr.execute("""
        ALTER TABLE product_attribute_value_product_template_attribute_line_rel
      RENAME COLUMN product_attribute_line_id
                 TO product_template_attribute_line_id
    """)

    util.remove_field(cr, "product.attribute.value", "product_ids")
    util.remove_field(cr, "product.attribute.value", "price_extra")
    # odoo/odoo@856c2e9008f1af7bc1327d9c2900db1e109ab0fa
    util.remove_field(cr, "product.attribute.value", "price_ids")
    util.remove_model(cr, "product.attribute.price")

    util.rename_xmlid(cr, "product.product_attribute_line_form", "product.product_template_attribute_line_form")
    util.remove_view(cr, "product.product_attribute_value_view_tree")
    util.remove_record(cr, "product.product_attribute_value_action")
    util.remove_view(cr, "product.assets_backend")

    util.force_noupdate(cr, "product.product_template_form_view", False)
