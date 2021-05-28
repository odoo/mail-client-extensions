# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "product.template", "life_time", "expiration_time")
    util.create_column(cr, "product_template", "use_expiration_date", "boolean")

    cr.execute(
        """
        UPDATE product_template
           SET use_expiration_date = GREATEST(expiration_time, 0)
                                   + GREATEST(use_time, 0)
                                   + GREATEST(removal_time, 0)
                                   + GREATEST(alert_time, 0)
                                   != 0
    """
    )
    cr.execute(
        """
        WITH lots AS (
            SELECT DISTINCT pp.product_tmpl_id AS id
              FROM stock_production_lot l
              JOIN product_product pp ON pp.id = l.product_id
          GROUP BY pp.product_tmpl_id, l.life_date, l.use_date, l.removal_date, l.alert_date
            HAVING l.life_date IS NOT NULL
                OR l.use_date IS NOT NULL
                OR l.removal_date IS NOT NULL
                OR l.alert_date IS NOT NULL
        )
        UPDATE product_template pt
           SET use_expiration_date = true
          FROM lots l
         WHERE l.id = pt.id
        """
    )

    util.rename_field(cr, "stock.production.lot", "life_date", "expiration_date")

    util.create_column(cr, "stock_move_line", "expiration_date", "timestamp")
    cr.execute(
        """
        UPDATE stock_move_line l
           SET expiration_date = t.expiration_date
          FROM stock_production_lot t
         WHERE t.id = l.lot_id
           AND t.expiration_date IS NOT NULL
           AND l.expiration_date IS NULL
    """
    )
