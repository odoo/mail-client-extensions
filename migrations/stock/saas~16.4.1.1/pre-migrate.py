# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "product.replenish", "route_ids")
    # Convert the reference to a stock_move.id on a stock_scrap to a reference to a stock_scrap.id on stock_move
    util.create_column(cr, "stock_move", "scrap_id", "int4")
    query = """
        UPDATE stock_move sm
           SET scrap_id = ss.id
          FROM stock_scrap ss
         WHERE ss.move_id = sm.id
    """
    util.explode_execute(cr, query, table="stock_move", alias="sm")
    util.remove_field(cr, "stock.move", "scrap_ids")
    util.remove_field(cr, "stock.scrap", "move_id")
    util.remove_field(cr, "stock.warehouse", "return_type_id")
