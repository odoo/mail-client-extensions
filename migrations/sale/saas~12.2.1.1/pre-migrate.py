# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "sale_order", "signed_on", "timestamp without time zone")
    util.remove_field(cr, "sale.order.line", "product_image")

    util.create_column(cr, "sale_advance_payment_inv", "deduct_down_payments", "boolean")
    util.create_column(cr, "sale_advance_payment_inv", "has_down_payments", "boolean")
    cr.execute(
        """
        UPDATE sale_advance_payment_inv
           SET advance_payment_method = 'delivered',
               deduct_down_payments = TRUE
         WHERE advance_payment_method = 'all'
    """
    )
