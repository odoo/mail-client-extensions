# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "pos_payment_method", "active", "boolean", default=True)
    util.create_column(cr, "pos_payment", "is_change", "boolean", default=False)
    util.create_column(cr, "pos_payment", "cardholder_name", "varchar")
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
    util.create_column(cr, "pos_config", "product_configurator", "boolean")
    util.create_column(cr, "pos_config", "manual_discount", "boolean", default=True)

    util.create_column(cr, "pos_order_line", "full_product_name", "varchar")

    util.create_column(cr, "pos_order", "is_tipped", "boolean")
    util.create_column(cr, "pos_order", "tip_amount", "numeric")

    cr.execute(
        """
          WITH tips AS (
            SELECT pos_order_line.order_id as order_id, pos_order_line.price_subtotal_incl as tip_amount
              FROM pos_order_line
              JOIN pos_order ON pos_order_line.order_id = pos_order.id
              JOIN pos_session ON pos_order.session_id = pos_session.id
              JOIN pos_config ON pos_session.config_id = pos_config.id
             WHERE pos_config.tip_product_id = pos_order_line.product_id
        )
        UPDATE pos_order
           SET tip_amount = tips.tip_amount, is_tipped = TRUE
          FROM tips
         WHERE tips.order_id = pos_order.id
        """
    )

    cr.execute("UPDATE pos_session SET state = 'opening_control' WHERE state = 'new_session'")
