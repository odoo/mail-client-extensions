from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_sale_picking.checkout_delivery")
