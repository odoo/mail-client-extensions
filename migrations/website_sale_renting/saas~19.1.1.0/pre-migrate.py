from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_sale_renting.products_collapsible")
    util.remove_view(cr, "website_sale_renting.o_wsale_offcanvas")
