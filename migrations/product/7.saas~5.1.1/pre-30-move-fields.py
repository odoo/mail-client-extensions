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

    # copy default values for taxes_id and supplier_taxes_id fields
    # (see odoo/odoo@285ba3d and odoo/odoo@96dd8bf)
    cr.execute("""INSERT INTO ir_values(user_id, company_id, model, name, key, key2, value, res_id)
                       SELECT user_id, company_id, 'product.template', name, key, key2, value,
                              CASE WHEN COALESCE(res_id, 0) = 0 THEN 0 ELSE
                                (SELECT product_tmpl_id FROM product_product WHERE id=v.res_id)
                              END
                         FROM ir_values v
                        WHERE model='product.product'
                          AND key='default'
                          AND name IN ('taxes_id', 'supplier_taxes_id')
               """)
