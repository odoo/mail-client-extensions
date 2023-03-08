# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr,
        "website_sale_mondialrelay.website_sale_delivery_mondialrelay_address_kanban",
        "website_sale_mondialrelay.website_sale_mondialrelay_address_kanban",
    )
    util.rename_xmlid(
        cr,
        "website_sale_mondialrelay.website_sale_delivery_mondialrelay_checkout",
        "website_sale_mondialrelay.website_sale_mondialrelay_checkout",
    )
    util.rename_xmlid(
        cr,
        "website_sale_mondialrelay.website_sale_delivery_mondialrelay_address_on_payment",
        "website_sale_mondialrelay.website_sale_mondialrelay_address_on_payment",
    )
    util.rename_xmlid(
        cr,
        "website_sale_mondialrelay.res_config_settings_view_form_inherit_website_sale_delivery_mondial_relay",
        "website_sale_mondialrelay.res_config_settings_view_form",
    )
    util.rename_xmlid(
        cr,
        "website_sale_mondialrelay.delivery_carrier_view_search_inherit_website_sale_delivery_mondialrelay",
        "website_sale_mondialrelay.delivery_carrier_view_search",
    )
