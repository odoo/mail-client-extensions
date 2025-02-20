from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_sale_ups.property_ups_carrier_account_inherit_portal_details")
