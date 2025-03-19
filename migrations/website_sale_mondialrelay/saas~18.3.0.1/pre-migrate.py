from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr,
        "website_sale_mondialrelay.website_sale_mondialrelay_address_on_payment",
        "website_sale_mondialrelay.address_on_checkout",
    )
