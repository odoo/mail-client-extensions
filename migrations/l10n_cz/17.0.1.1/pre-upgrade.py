from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_move", "taxable_supply_date", "date")
    query = """
        UPDATE account_move
           SET taxable_supply_date = date
         WHERE date IS NOT NULL
    """
    util.explode_execute(cr, query, table="account_move")
