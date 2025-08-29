from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(
        cr,
        "sale.order",
        "fedex_access_point_address",
        "website_delivery_fedex",
        "website_sale",
    )
    util.rename_field(cr, "sale.order", "fedex_access_point_address", "access_point_address")
    if util.column_exists(cr, "sale_order", "access_point_address"):
        cr.execute(
            """
                 ALTER TABLE sale_order
                ALTER COLUMN access_point_address TYPE jsonb
                       USING access_point_address::jsonb
            """
        )

    util.remove_view(
        cr,
        "website_sale.payment_delivery_shipping_method",
    )
    util.rename_xmlid(
        cr,
        "website_sale.view_delivery_carrier_search_inherit_website_sale_delivery",
        "website_sale.view_delivery_carrier_search",
    )
    util.rename_xmlid(
        cr,
        "website_sale.view_delivery_carrier_tree_inherit_website_sale_delivery",
        "website_sale.view_delivery_carrier_tree",
    )
    if not util.version_gte("saas~16.3"):
        util.create_column(cr, "sale_order", "amount_delivery", "numeric", default=0)
