from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT sc.id,
               sc.name->>'en_US',
               shp.name,
               ret.name
          FROM delivery_carrier sc
     LEFT JOIN sendcloud_shipping_product shp
            ON shp.id = sc.sendcloud_shipping_id
     LEFT JOIN sendcloud_shipping_product ret
            ON ret.id = sc.sendcloud_return_id
         WHERE sc.delivery_type = 'sendcloud'
        """
    )
    sc_carriers = []
    for cid, name, shipping_method, return_method in cr.fetchall():
        str_list = ["<li>", util.get_anchor_link_to_record("delivery.carrier", cid, name)]
        if shipping_method or return_method:
            str_list.append("<ul>")
            if shipping_method:
                str_list.append("<li>Shipping: {}</li>".format(shipping_method))
            if return_method:
                str_list.append("<li>Return: {}</li>".format(return_method))
            str_list.append("</ul>")
        str_list.append("</li>")
        sc_carriers.append("".join(str_list))

    # As from now one, a sendcloud delivery carrier relies on 'product' rather than 'method'
    # and as a sendcloud product is a set of method, we should ideally request the Sendcloud API
    # in order to know by which products we can replace the already defined methods.
    # However, that would be a bad practice in a migration script to rely on a external API,
    # and anyway, it's not allowed by the framework.
    # Instead, we warn the user of this change such that he can reconfigure his carriers afterwards
    util.add_to_migration_reports(
        category="Sendcloud Delivery Carrier",
        message="""
            <details>
            <summary>
            The Sendcloud Delivery Carrier has been updated and now relies on a Sendcloud's product rather than a method.<br/>
            As the conversion of you're actual configuration would requires an acces to external and inconsistent data, it can't be achieved automatically.
            </summary>
            You will have to manually update the following delivery carrier(s):
            <ul>
            {}
            </ul>
            </details>
        """.format(
            "\n".join(sc_carriers)
        ),
        format="html",
    )
    # Theoretically not optimal but practically more than : fetching & nulling references, deleting FK; truncate table; recreating FK
    cr.execute(
        """
            DELETE FROM sendcloud_shipping_product
        """
    )

    # Update sendcloud.shipping.product model
    # N.B. We don't force computation as we ensured the table is empty
    util.remove_field(cr, "sendcloud.shipping.product", "sendcloud_id")
    util.create_column(cr, "sendcloud_shipping_product", "sendcloud_code", "char")
    util.create_column(cr, "sendcloud_shipping_product", "functionalities", "jsonb")
    util.create_column(cr, "sendcloud_shipping_product", "can_customize_functionalities", "bool")
    util.create_column(cr, "sendcloud_shipping_product", "has_multicollo", "bool")
    util.alter_column_type(cr, "sendcloud_shipping_product", "max_weight", "integer")
    util.alter_column_type(cr, "sendcloud_shipping_product", "min_weight", "integer")

    # Update sendcloud.shipping.wizard model
    util.remove_field(cr, "sendcloud.shipping.wizard", "shipping_product")
    util.remove_field(cr, "sendcloud.shipping.wizard", "ship_carrier")
    util.remove_field(cr, "sendcloud.shipping.wizard", "ship_min_weight")
    util.remove_field(cr, "sendcloud.shipping.wizard", "ship_max_weight")
    util.remove_field(cr, "sendcloud.shipping.wizard", "ship_country_ids")
    util.remove_field(cr, "sendcloud.shipping.wizard", "return_product")
    util.remove_field(cr, "sendcloud.shipping.wizard", "return_carrier")
    util.remove_field(cr, "sendcloud.shipping.wizard", "return_min_weight")
    util.remove_field(cr, "sendcloud.shipping.wizard", "return_max_weight")
    util.remove_field(cr, "sendcloud.shipping.wizard", "return_country_ids")
    util.create_column(cr, "sendcloud_shipping_wizard", "shipping_products", "jsonb")
    util.create_column(cr, "sendcloud_shipping_wizard", "return_products", "jsonb")
    util.create_column(cr, "sendcloud_shipping_wizard", "sendcloud_products_code", "jsonb")

    # Update stock.picking
    # N.B. As multicollo wasn't implemented before, it is safe to transform existing refs into list<int> : "1,2,3" -> [1,2,3]
    cr.execute(
        """
        create function sendcloud_csv_to_jsonb(text) returns jsonb as $$
        begin
            return to_jsonb(string_to_array($1, ',')::int[]);
        exception when others then
            return NULL;
        end;
        $$ LANGUAGE plpgsql IMMUTABLE RETURNS NULL ON NULL INPUT PARALLEL SAFE;
    """
    )
    util.alter_column_type(cr, "stock_picking", "sendcloud_parcel_ref", "jsonb", using="sendcloud_csv_to_jsonb({0})")
    util.alter_column_type(
        cr, "stock_picking", "sendcloud_return_parcel_ref", "jsonb", using="sendcloud_csv_to_jsonb({0})"
    )

    cr.execute("DROP FUNCTION sendcloud_csv_to_jsonb(text)")

    # Update delivery.carrier
    util.create_column(
        cr, "delivery_carrier", "country_id", "integer", fk_table="res_country", on_delete_action="SET NULL"
    )
    util.create_column(cr, "delivery_carrier", "sendcloud_shipping_name", "varchar")
    util.create_column(cr, "delivery_carrier", "sendcloud_return_name", "varchar")
    util.create_column(cr, "delivery_carrier", "sendcloud_product_functionalities", "jsonb")
    util.create_column(cr, "delivery_carrier", "sendcloud_use_batch_shipping", "bool")

    # If any value is set, then update to True, else update to False
    util.alter_column_type(cr, "delivery_carrier", "sendcloud_shipping_rules", "boolean", using="{0} IS NOT NULL")

    # Update domains based on 'sendcloud_shipping_rules'
    # (..., '=', False) => (..., '=', False)
    # (*)               => (..., '=', True)
    def adapter(leaf, _or, _neg):
        left, op, right = leaf
        if not (op == "=" and right is False):
            return [left, "=", True]
        return leaf

    util.domains.adapt_domains(
        cr, "delivery.carrier", "sendcloud_shipping_rules", "sendcloud_shipping_rules", adapter=adapter
    )
