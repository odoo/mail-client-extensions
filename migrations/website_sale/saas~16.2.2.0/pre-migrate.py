from odoo.upgrade import util


def migrate(cr, version):

    util.rename_xmlid(cr, "website_sale.menu_ecommerce_payment_icons", "website_sale.menu_ecommerce_payment_methods")
