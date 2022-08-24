# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        INSERT INTO stock_notification_product_partner_rel(product_product_id, res_partner_id)
             SELECT product_id, partner_id
               FROM product_wishlist
              WHERE partner_id IS NOT NULL AND stock_notification IS TRUE
        """
    )
    util.remove_column(cr, "product_wishlist", "stock_notification")
