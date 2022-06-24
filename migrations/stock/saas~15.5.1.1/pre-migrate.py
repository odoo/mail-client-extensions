from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "stock_location", "replenish_location", "boolean")
    query = """
        UPDATE stock_location l
           SET replenish_location = true
          FROM stock_warehouse w
         WHERE l.id = w.lot_stock_id
           AND l.usage = 'internal'
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="stock_location", alias="l"))
