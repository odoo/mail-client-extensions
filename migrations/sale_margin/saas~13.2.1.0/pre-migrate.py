# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sale_order_line", "margin_percent", "float8")
    cr.execute(
        """
        UPDATE sale_order_line
           SET margin_percent = CASE WHEN COALESCE(price_subtotal, 0) = 0 THEN 0
                                     ELSE margin / price_subtotal
                                 END
    """
    )
    util.create_column(cr, "sale_order", "margin_percent", "float8")
    cr.execute(
        """
        WITH sol AS (
            SELECT order_id, sum(margin) as margin
              FROM sale_order_line
          GROUP BY order_id
        )
        UPDATE sale_order so
           SET margin = sol.margin,
               margin_percent = CASE WHEN COALESCE(so.amount_untaxed, 0) = 0 THEN 0
                                     ELSE sol.margin / so.amount_untaxed
                                 END
          FROM sol
         WHERE sol.order_id = so.id
    """
    )
