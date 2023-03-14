from odoo.upgrade import util


def migrate(cr, version):
    # Change the selection ('KM' and 'MI')  to UOM
    # Field to change : fedex_locations_radius_unit

    id_uom_km = util.ref(cr, "uom.product_uom_km")
    id_uom_mi = util.ref(cr, "uom.product_uom_mile")

    cr.execute(
        """
            ALTER TABLE delivery_carrier
                ALTER fedex_locations_radius_unit TYPE integer
                USING CASE WHEN fedex_locations_radius_unit = 'MI' THEN %s ELSE %s END
        """,
        [id_uom_mi, id_uom_km],
    )

    util.remove_view(
        cr,
        "website_sale_fedex.payment_delivery_methods_inherit_website_sale_delivery",
    )
    util.remove_record(cr, "website_sale_fedex.selection__delivery_carrier__fedex_locations_radius_unit__km")
    util.remove_record(cr, "website_sale_fedex.selection__delivery_carrier__fedex_locations_radius_unit__mi")
