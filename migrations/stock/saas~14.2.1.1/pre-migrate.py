# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    # Set a in_date, of quant without in_date, to the min of date because NULL was considered older
    cr.execute(
        """
    UPDATE stock_quant
       SET in_date = (SELECT coalesce(min(in_date) - interval '1s', now() at time zone 'utc') FROM stock_quant)
     WHERE in_date IS NULL
        """
    )

    util.delete_unused(cr, "stock.sequence_tracking")
    cr.execute(
        """
        UPDATE stock_move AS sm
           SET picking_type_id = sp.picking_type_id
          FROM stock_picking AS sp
         WHERE sp.id = sm.picking_id
        """
    )
