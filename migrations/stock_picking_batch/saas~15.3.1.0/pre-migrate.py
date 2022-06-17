# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "stock_move_line", "batch_id", "int4")

    query = """
        UPDATE stock_move_line l
           SET batch_id = p.batch_id
          FROM stock_picking p
         WHERE l.picking_id = p.id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="stock_move_line", alias="l"))
