# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "sale.order", "delivery_price")
    util.remove_field(cr, "sale.order", "available_carrier_ids")

    util.create_column(cr, "sale_order", "recompute_delivery_price", "boolean")
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
        UPDATE sale_order s
           SET recompute_delivery_price = TRUE
          FROM sale_order_line l
         WHERE s.state IN ('draft', 'sent')
           AND l.order_id = s.id
           AND l.is_delivery = TRUE
            """,
            table="sale_order",
            alias="s",
        ),
    )
    cr.execute("UPDATE sale_order SET recompute_delivery_price = FALSE WHERE recompute_delivery_price IS NULL")
