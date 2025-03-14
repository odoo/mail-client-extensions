from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "purchase_stock.product_category_view_form")
