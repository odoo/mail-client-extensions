# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # move the rental values into temp columns and in post, update the values
    cr.execute(
        """
        UPDATE sale_order_line SET start_date=pickup_date,next_invoice_date=return_date
         WHERE pickup_date IS NOT NULL
        """
    )
    util.remove_field(cr, "sale.order.line", "pickup_date")
    util.remove_field(cr, "product.template", "rental_pricing_ids")
    util.remove_field(cr, "product.product", "rental_pricing_ids")
