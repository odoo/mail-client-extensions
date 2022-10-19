# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "stock_move_line", "carrier_id", "int4")
    query = """
        UPDATE stock_move_line sml
           SET carrier_id = sp.carrier_id
          FROM stock_picking sp
         WHERE sml.picking_id = sp.id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="stock_move_line", alias="sml"))
    util.update_field_references(cr, "carrier_name", "carrier_id", ("stock.move.line",))

    util.remove_field(cr, "stock.move.line", "carrier_name")
