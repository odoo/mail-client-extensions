# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # manual update of noupdate records
    product = util.ref(cr, "event_sale.product_product_event")
    cr.execute(
        """
        UPDATE product_product
           SET default_code = 'EVENT_REG'
         WHERE default_code IS NULL
           AND id = %s
    """,
        [product],
    )
    cr.execute(
        """
        UPDATE product_template t
           SET categ_id = %s
          FROM product_product p
         WHERE p.product_tmpl_id = t.id
           AND p.id = %s
    """,
        [util.ref(cr, "event_sale.product_category_events"), product],
    )
