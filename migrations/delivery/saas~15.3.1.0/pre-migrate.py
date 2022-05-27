# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "stock_move_line", "carrier_name", "varchar")

    query = """
        UPDATE stock_move_line l
           SET carrier_name = d.name
          FROM stock_picking sp
          JOIN delivery_carrier d ON sp.carrier_id = d.id
         WHERE l.picking_id = sp.id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="stock_move_line", alias="l"))
