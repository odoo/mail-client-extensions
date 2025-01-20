from odoo.upgrade import util


def migrate(cr, version):
    util.delete_unused(
        cr, "website_sale_shiprocket.shiprocket_payment_method_cash_on_delivery", deactivate=True, keep_xmlids=False
    )
    util.delete_unused(
        cr, "website_sale_shiprocket.payment_provider_shiprocket_cod", deactivate=True, keep_xmlids=False
    )
    util.remove_module(cr, "website_sale_shiprocket")
