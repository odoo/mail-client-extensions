from odoo.upgrade import util


def migrate(cr, version):
    query = "UPDATE stock_picking SET create_date = date WHERE create_date IS NULL AND date IS NOT NULL"
    util.explode_execute(cr, query, table="stock_picking")
    util.update_field_usage(cr, "stock.picking", "date", "create_date")
    util.remove_field(cr, "stock.picking", "date")
