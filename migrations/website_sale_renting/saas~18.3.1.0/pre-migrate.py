from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_sale_renting.website_sale_renting_period")
