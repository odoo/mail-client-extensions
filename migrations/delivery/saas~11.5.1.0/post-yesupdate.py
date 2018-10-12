# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # manual update of noupdate records
    product = util.ref(cr, "delivery.product_product_delivery")
    cr.execute(
        """
        UPDATE product_product
           SET default_code = 'Delivery_007'
         WHERE default_code = 'Delivery'
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
           AND p.id IN %s
    """,
        [
            util.ref(cr, "delivery.product_category_deliveries"),
            (
                product,
                # and demo data, just in case
                util.ref(cr, "delivery.product_product_delivery_poste"),
                util.ref(cr, "delivery.product_product_delivery_normal"),
            ),
        ],
    )
