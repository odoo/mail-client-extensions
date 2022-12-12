from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(
        cr,
        "sale.order",
        "fedex_access_point_address",
        "website_delivery_fedex",
        "website_sale_delivery",
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
        "website_sale_delivery.payment_delivery_shipping_method",
    )
