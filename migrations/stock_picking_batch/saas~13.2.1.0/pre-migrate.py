# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "stock_picking_batch", "picking_type_id", "integer")
    cr.execute(
        """
        WITH p AS (
            SELECT batch_id, min(picking_type_id) as picking_type_id
              FROM stock_picking
             WHERE batch_id IS NOT NULL
               AND picking_type_id IS NOT NULL
          GROUP BY batch_id
            HAVING count(picking_type_id) = 1
        )
        UPDATE stock_picking_batch b
           SET picking_type_id = p.picking_type_id
          FROM p
         WHERE p.batch_id = b.id
    """
    )

    util.create_column(cr, "stock_picking_to_batch", "mode", "varchar")
    util.create_column(cr, "stock_picking_to_batch", "user_id", "integer")
