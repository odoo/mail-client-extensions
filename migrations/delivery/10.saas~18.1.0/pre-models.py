# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'delivery_carrier', 'name', 'varchar')
    util.create_column(cr, 'delivery_carrier', 'active', 'boolean')
    util.create_column(cr, 'delivery_carrier', 'debug_logging', 'boolean')
    util.create_column(cr, 'delivery_carrier', 'company_id', 'int4')

    cr.execute("""
        UPDATE delivery_carrier c
           SET debug_logging = false,
               name = t.name,
               active = p.active,
               company_id = t.company_id
          FROM product_product p, product_template t
         WHERE c.product_id = p.id
           AND p.product_tmpl_id = t.id
    """)

    util.remove_field(cr, 'delivery_price_rule', 'standard_price')
