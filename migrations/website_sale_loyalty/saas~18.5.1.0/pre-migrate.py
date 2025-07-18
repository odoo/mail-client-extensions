from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_sale_loyalty.website_sale_coupon_cart_hide_qty")
