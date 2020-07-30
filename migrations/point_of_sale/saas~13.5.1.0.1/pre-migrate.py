# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "pos_payment", "is_change", "boolean", default=False)
    util.create_column(cr, "pos_payment", "ticket", "varchar")

    # Change payments are the negative cash payments in orders with positive amount.
    # We set the is_change to TRUE for these payments.
    cr.execute(
        """
        WITH change_payments AS (
            SELECT payment.id as id
              FROM pos_payment payment
              JOIN pos_payment_method method ON payment.payment_method_id = method.id
              JOIN pos_order _order ON payment.pos_order_id = _order.id
             WHERE method.is_cash_count = TRUE AND _order.amount_total > 0 AND payment.amount < 0
        )
        UPDATE pos_payment
           SET is_change = TRUE
          FROM change_payments
         WHERE change_payments.id = pos_payment.id
    """
    )

    util.rename_field(cr, "pos.config", "module_pos_reprint", "manage_orders")

    util.create_column(cr, "pos_order_line", "full_product_name", "varchar")
