from odoo.upgrade import util


def migrate(cr, version):
    util.delete_unused(cr, "pos_restaurant.product_category_pos_food")
