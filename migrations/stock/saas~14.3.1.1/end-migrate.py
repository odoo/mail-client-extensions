# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        UPDATE stock_rule sr
           SET propagate_carrier = True
          FROM stock_warehouse sw
         WHERE sr.route_id = sw.delivery_route_id
           AND sr.propagate_carrier IS NOT TRUE
        """
    )
