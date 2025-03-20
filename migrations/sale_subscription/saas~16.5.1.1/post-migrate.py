from odoo.upgrade import util


def migrate(cr, version):
    # Will be removed at the end but are needed for easier reference
    util.create_column(cr, "sale_subscription_pricing", "old_id", "int4")

    # Update reference on Alerts
    cr.execute(
        """
    INSERT INTO sale_order_alert_sale_subscription_plan_rel (sale_subscription_plan_id, sale_order_alert_id)
         SELECT ssp.id AS plan_id,
                trel.sale_order_alert_id AS sale_order_alert_id
           FROM sale_order_alert_sale_order_template_rel trel
           JOIN sale_subscription_plan ssp
             ON ssp.template_id = trel.sale_order_template_id
    """
    )

    # Create sale subscription pricing
    cr.execute(
        """
    INSERT INTO sale_subscription_pricing (old_id, price, currency_id, plan_id, product_template_id, pricelist_id)
    SELECT pp.id AS old_id,
           COALESCE(pp.price, 1) AS price,
           pp.currency_id AS currency_id,
           ssp.id AS plan_id,
           pp.product_template_id AS product_template_id,
           pp.pricelist_id AS pricelist_id
      FROM product_pricing pp
      JOIN sale_subscription_plan ssp
        ON pp.recurrence_id = ssp.recurrence_id
 LEFT JOIN product_pricelist pl
        ON pp.pricelist_id = pl.id
     WHERE pp.pricelist_id IS NULL
        OR pl.company_id IS NULL
        OR ssp.company_id IS NULL
        OR pl.company_id = ssp.company_id
    """
    )

    # Create sale subscription pricing Product M2M
    cr.execute(
        """
    INSERT INTO product_product_sale_subscription_pricing_rel (
           product_product_id,
           sale_subscription_pricing_id
           )
    SELECT rel.product_product_id AS product_product_id,
           ssp.id AS sale_subscription_pricing_id
      FROM product_pricing_product_product_rel rel
      JOIN sale_subscription_pricing ssp ON rel.product_pricing_id = ssp.old_id
    """
    )

    # Remove columns/fields that were kept for reference
    util.remove_column(cr, "sale_subscription_plan", "template_id")
    util.remove_column(cr, "sale_subscription_plan", "pause")
    util.remove_column(cr, "sale_subscription_plan", "recurrence_id")
    util.remove_column(cr, "sale_subscription_pricing", "old_id")

    util.remove_field(cr, "sale.order.alert", "subscription_template_ids")

    if not util.module_installed(cr, "sale_renting"):
        # Remove tables that were kept from sale_temporal module in base
        cr.execute("DROP TABLE IF EXISTS product_pricing_product_product_rel")
        for model in ["sale.temporal.recurrence", "product.pricing"]:
            table = util.table_of_model(cr, model)
            cr.execute(util.format_query(cr, "DROP TABLE IF EXISTS {} CASCADE", table))
