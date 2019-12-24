# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.force_noupdate(cr, 'product.property_product_pricelist', True)

    # ensure uom constraint can be set
    cr.execute("UPDATE product_uom SET rounding=0.001 WHERE coalesce(rounding, 0) = 0")
    cr.execute("UPDATE product_uom SET rounding=abs(rounding)")

    util.remove_field(cr, 'product.template', 'product_manager')

    # fix m2m definitions
    cr.execute("""
        ALTER TABLE product_attribute_value_product_product_rel RENAME COLUMN prod_id TO product_product_id;
        ALTER TABLE product_attribute_value_product_product_rel RENAME COLUMN att_id TO product_attribute_value_id;

        ALTER TABLE product_attribute_line_product_attribute_value_rel RENAME COLUMN line_id TO product_attribute_line_id;
        ALTER TABLE product_attribute_line_product_attribute_value_rel RENAME COLUMN val_id TO product_attribute_value_id;
    """)

    # pre compute the field product_template.default_code
    util.create_column(cr, 'product_template', 'default_code', 'varchar')

    cr.execute("""
    UPDATE product_template pt SET default_code = A.default_code
    FROM (
        SELECT pt.id pt_id, min(pp.default_code) default_code
        FROM product_template pt
        JOIN product_product pp ON pt.id = pp.product_tmpl_id
        WHERE pp.active = 't'
        GROUP BY pt.id
        HAVING count(*) = 1 AND min(pp.default_code) IS NOT NULL
    )A
    WHERE pt.id = A.pt_id
    """)

    cr.execute("UPDATE product_template pt SET default_code = '' WHERE default_code IS NULL")

