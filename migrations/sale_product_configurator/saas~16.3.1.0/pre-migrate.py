from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    xmlids = [
        "optional_products_modal",
        "product_quantity_config",
        "configure",
        "configure_optional_products",
        "optional_product_items",
    ]
    if util.module_installed(cr, "website_sale_product_configurator"):
        for xmlid in xmlids:
            util.rename_xmlid(
                cr,
                *eb("{,website_}sale_product_configurator." + xmlid),
            )
    else:
        for xmlid in xmlids:
            util.remove_view(cr, "sale_product_configurator." + xmlid)
