from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr,
        "website_sale_ups.payment_provider_ups_cod",
        "delivery.payment_provider_cod",
    )
    util.rename_xmlid(
        cr,
        "website_sale_ups.payment_method_cash_on_delivery",
        "delivery.payment_method_cash_on_delivery",
    )
