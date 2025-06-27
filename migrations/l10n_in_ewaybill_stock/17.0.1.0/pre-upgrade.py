from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "stock_move", "ewaybill_price_unit", "numeric")
    util.create_m2m(cr, "account_tax_stock_move_rel", "stock_move", "account_tax")
