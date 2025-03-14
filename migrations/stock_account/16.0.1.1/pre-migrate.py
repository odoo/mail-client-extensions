from odoo.upgrade import util


def migrate(cr, version):
    query = """
        UPDATE account_move_line line
           SET display_type = 'cogs'
         WHERE line.is_anglo_saxon_line
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_move_line", alias="line"))

    util.remove_field(cr, "account.move.line", "is_anglo_saxon_line")
