from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "repair_order", "currency_id", "integer")
    query = """
        WITH ro as (
           SELECT r.id, COALESCE(p.currency_id, c.currency_id) as currency_id
             FROM repair_order r
             JOIN res_company c
               ON c.id = r.company_id
        LEFT JOIN product_pricelist p
               ON p.id = r.pricelist_id
            WHERE {parallel_filter}
        )
        UPDATE repair_order r
           SET currency_id = ro.currency_id
          FROM ro
         WHERE ro.id = r.id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, alias="r", table="repair_order"))
