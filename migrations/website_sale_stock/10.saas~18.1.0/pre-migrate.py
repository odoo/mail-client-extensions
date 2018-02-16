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

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb('website_sale_stock.{orders_followup,portal_order_page}_shipping'))
