from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_sale.optional_product_items")
    util.remove_view(cr, "website_sale.configure_optional_products")
    util.remove_view(cr, "website_sale.product_quantity_config")
    util.remove_view(cr, "website_sale.optional_products_modal")
