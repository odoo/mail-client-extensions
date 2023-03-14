from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr, "website_sale_ups.payment_delivery_inherit_website_sale_delivery", "website_sale_ups.payment_delivery"
    )
    util.rename_xmlid(
        cr,
        "website_sale_ups.payment_delivery_methods_inherit_website_sale_delivery",
        "website_sale_ups.payment_delivery_methods",
    )
    util.rename_xmlid(
        cr,
        "website_sale_ups.res_config_settings_view_form_inherit_website_delivery_ups",
        "website_sale_ups.res_config_settings_view_form",
    )
