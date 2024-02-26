from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.analytic.line", "allowed_so_line_ids")

    query = """
        UPDATE product_document
        SET attached_on = 'hidden'
        WHERE attached_on is NULL
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="product_document"))
