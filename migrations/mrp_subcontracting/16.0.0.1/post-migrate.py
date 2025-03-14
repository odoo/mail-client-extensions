from odoo.upgrade import util


def migrate(cr, version):
    query = """
        UPDATE stock_location l
           SET is_subcontracting_location = true
          FROM res_company c
         WHERE l.id = c.subcontracting_location_id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="stock_location", alias="l"))
