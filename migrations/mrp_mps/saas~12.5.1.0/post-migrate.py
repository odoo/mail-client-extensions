# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
        WITH min_dates as (
            SELECT order_id, min(date_planned) as min_date
              FROM purchase_order_line
          GROUP BY order_id
        )
        UPDATE purchase_order p
           SET date_planned_mps=min_dates.min_date
          FROM min_dates
         WHERE min_dates.order_id=p.id
        """
    )
    cr.execute(
        """
        UPDATE purchase_order
           SET date_planned_mps=date_order
         WHERE date_planned_mps IS NULL
        """
    )
