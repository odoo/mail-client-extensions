from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale_stock_renting.rental_stock_sale_order_form")
