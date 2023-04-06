# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "sale.coupon.program", "order_line_ids")

    util.create_m2m(cr, "product_product_sale_coupon_reward_rel", "product_product", "sale_coupon_reward")
    cr.execute(
        """
        INSERT INTO product_product_sale_coupon_reward_rel(product_product_id, sale_coupon_reward_id)
             SELECT discount_specific_product_id, id
               FROM sale_coupon_reward
              WHERE discount_specific_product_id IS NOT NULL
    """
    )
    # NOTE: sale.coupon.program inheritS from sale.coupon.reward
    util.update_field_usage(
        cr,
        "sale.coupon.reward",
        "discount_specific_product_id",
        "discount_specific_product_ids",
    )
    util.remove_field(cr, "sale.coupon.reward", "discount_specific_product_id")

    cr.execute(
        """
        UPDATE sale_coupon_reward
           SET discount_apply_on = 'specific_products' WHERE discount_apply_on = 'specific_product'
    """
    )
