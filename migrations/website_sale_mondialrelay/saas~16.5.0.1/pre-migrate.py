from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_sale_mondialrelay.website_sale_mondialrelay_checkout")
