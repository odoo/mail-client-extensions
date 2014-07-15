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
