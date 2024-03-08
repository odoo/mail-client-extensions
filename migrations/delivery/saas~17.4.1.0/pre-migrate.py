from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "website_sale"):
        util.move_field_to_module(cr, "sale.order", "access_point_address", "website_sale", "delivery")
        util.rename_field(cr, "sale.order", "access_point_address", "pickup_location_data")
