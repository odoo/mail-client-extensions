from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_sale_renting.cart_summary_inherit_website_sale_renting")
