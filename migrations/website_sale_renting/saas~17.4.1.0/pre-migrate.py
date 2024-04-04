from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_sale_renting.optional_product_items")
    util.remove_view(cr, "website_sale_renting.configure_optional_products")
