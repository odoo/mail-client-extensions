from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_event_sale.cart_popover_inherit_website_event_sale")
