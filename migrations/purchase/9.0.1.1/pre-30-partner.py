# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # convert property field from product.pricelist to res.currency

    util.rename_field(cr, 'res.partner',
                      'property_product_pricelist_purchase',
                      'property_purchase_currency_id')

    cr.execute("""
        UPDATE ir_model_fields
           SET relation='res.currency'
         WHERE model='res.partner'
           AND name='property_purchase_currency_id'
     RETURNING id
    """)
    [fields_id] = cr.fetchone() or [None]
    cr.execute("""
        UPDATE ir_property p
           SET value_reference = CONCAT('res.currency,', l.currency_id)
          FROM product_pricelist l
         WHERE p.fields_id = %s
           AND p.value_reference IS NOT NULL
           AND l.id = substring(p.value_reference FROM '%%,#"%%#"' FOR '#')::integer
    """, [fields_id])
