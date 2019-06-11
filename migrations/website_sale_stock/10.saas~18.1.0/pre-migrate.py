# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
        UPDATE product_template
           SET inventory_availability = CASE WHEN inventory_availability = 'empty' THEN 'never'
                                             WHEN inventory_availability = 'in_stock' THEN 'always'
                                             WHEN inventory_availability = 'warning' THEN 'custom'
                                             ELSE inventory_availability
                                         END
    """)

    cr.execute("""
        UPDATE ir_default
           SET json_value = CASE WHEN json_value = '"empty"' THEN '"never"'
                                 WHEN json_value = '"in_stock"' THEN '"always"'
                                 WHEN json_value = '"warning"' THEN '"custom"'
                                 ELSE json_value
                             END
         WHERE field_id = (SELECT id FROM ir_model_fields
                            WHERE name='inventory_availability'
                             AND model='product.template')
    """)

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb('website_sale_stock.{orders_followup,portal_order_page}_shipping'))
