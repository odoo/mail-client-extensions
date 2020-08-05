# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "stock_picking_batch", "scheduled_date", "timestamp without time zone")
    cr.execute(
        """
        WITH pick AS (
              SELECT batch_id, MIN(scheduled_date) as scheduled_date
                FROM stock_picking
               WHERE batch_id IS NOT NULL
            GROUP BY batch_id
        )
        UPDATE stock_picking_batch spb
           SET scheduled_date = pick.scheduled_date
          FROM pick
         WHERE pick.batch_id = spb.id
        """
    )
