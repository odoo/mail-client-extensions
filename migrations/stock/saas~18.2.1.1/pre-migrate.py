from odoo.upgrade import util


def migrate(cr, version):
    query = """
        UPDATE stock_quant sq
            SET inventory_diff_quantity = 0
        WHERE inventory_quantity_set IS NOT TRUE
        """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="stock_quant", alias="sq"))
