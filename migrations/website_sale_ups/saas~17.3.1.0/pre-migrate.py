from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_sale_ups.checkout_delivery")
    util.rename_xmlid(cr, "website_sale_ups.payment_delivery_methods", "website_sale_ups.ups_delivery_method")
