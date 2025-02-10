from odoo.upgrade import util


def migrate(cr, version):
    util.change_field_selection_values(cr, "delivery.carrier", "delivery_type", {"onsite": "in_store"})
    util.change_field_selection_values(cr, "payment.provider", "custom_mode", {"onsite": "on_site"})
    util.remove_field(cr, "website", "picking_site_ids")
    util.remove_field(cr, "res.config.settings", "picking_site_ids")

    cr.execute(
        """
        UPDATE delivery_carrier
           SET is_published = FALSE
         WHERE delivery_type = 'in_store'
           AND warehouse_id IS NULL
        """
    )

    util.create_m2m(cr, "delivery_carrier_stock_warehouse_rel", "delivery_carrier", "stock_warehouse")
    cr.execute(
        """
        INSERT INTO delivery_carrier_stock_warehouse_rel(delivery_carrier_id, stock_warehouse_id)
             SELECT id, warehouse_id
               FROM delivery_carrier
              WHERE warehouse_id IS NOT NULL
    """
    )
    util.remove_column(cr, "delivery_carrier", "warehouse_id")
    util.rename_field(cr, "delivery.carrier", "warehouse_id", "warehouse_ids")

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("website_sale_collect.payment_provider_{onsite,on_site}"))
    util.rename_xmlid(cr, *eb("website_sale_collect.{onsite_delivery_product,product_pick_up_in_store}"))
    util.rename_xmlid(cr, *eb("website_sale_collect.{default_onsite_carrier,carrier_pick_up_in_store}"))
    util.rename_xmlid(
        cr, *eb("website_sale_collect.{view_delivery_carrier_form_with_onsite_picking,delivery_carrier_form}")
    )
    util.rename_xmlid(cr, *eb("website_sale_collect.res_config_settings{_view,}_form"))
    util.remove_record(cr, "website_sale_collect.payment_method_form")
