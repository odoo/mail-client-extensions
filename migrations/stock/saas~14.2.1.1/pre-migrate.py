# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    # Set a in_date, of quant without in_date, to the min of date because NULL was considered older
    cr.execute("SELECT coalesce(min(in_date) - interval '1s', now() at time zone 'utc') FROM stock_quant")
    (min_date,) = cr.fetchone()
    query = cr.mogrify("UPDATE stock_quant SET in_date = %s WHERE in_date IS NULL", [min_date]).decode()
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="stock_quant"))

    util.delete_unused(cr, "stock.sequence_tracking")
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
            UPDATE stock_move AS sm
               SET picking_type_id = sp.picking_type_id
              FROM stock_picking AS sp
             WHERE sp.id = sm.picking_id
            """,
            table="stock_move",
            alias="sm",
        ),
    )

    util.remove_field(cr, "stock.move", "note")
    util.remove_field(cr, "stock.move", "picking_partner_id")
    util.remove_field(cr, "stock.move", "backorder_id")
