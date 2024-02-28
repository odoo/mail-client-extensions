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
    util.create_column(cr, "stock_lot", "lot_properties", "jsonb")
    util.create_column(cr, "stock_lot", "location_id", "integer")
    cr.execute(
        """
        WITH filtered_lots AS(
            SELECT lot.id AS lot_id,
                   min(quant.location_id) AS location_id
              FROM stock_lot lot
              JOIN stock_quant quant
                ON lot.id = quant.lot_id
             WHERE quant.quantity > 0
          GROUP BY lot.id
            HAVING count(*) = 1
        )
        UPDATE stock_lot sl
           SET location_id = fl.location_id
          FROM filtered_lots fl
         WHERE sl.id = fl.lot_id
    """
    )
