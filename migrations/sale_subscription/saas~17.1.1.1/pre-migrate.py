# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sale_subscription_pricing", "active", "boolean", default=True)

    cr.execute(
        """
        UPDATE sale_subscription_pricing sub_pricing
           SET active = False
          FROM product_pricelist pricelist
         WHERE sub_pricing.pricelist_id = pricelist.id
           AND pricelist.active IS NOT True
    """
    )
