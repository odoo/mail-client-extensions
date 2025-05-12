from odoo.upgrade import util


def migrate(cr, version):
    # Compute sequence on sale_subscription_plans
    util.create_column(cr, "sale_subscription_plan", "sequence", "int4")
    cr.execute("""
        UPDATE sale_subscription_plan
               SET sequence = billing_period_value * CASE billing_period_unit
                                                          WHEN 'year'  THEN 52
                                                          WHEN 'month' THEN 4
                                                          WHEN 'week'  THEN 1
                                                          ELSE              1
                                                      END
    """)

    # Migrate sale.subscription.pricing into product.pricelist.item
    util.create_column(cr, "product_pricelist_item", "plan_id", "int4")
    util.create_column(cr, "product_pricelist_item", "_upg_pricing_id", "int4")

    cr.execute(
        """
            INSERT INTO product_pricelist_item(
                               _upg_pricing_id,
                               plan_id, pricelist_id, company_id,
                               currency_id, fixed_price,
                               product_tmpl_id, product_id,
                               applied_on,
                               display_applied_on, base, compute_price
                )
                    SELECT p.id,
                           p.plan_id, p.pricelist_id, plan.company_id,
                           p.currency_id, p.price,
                           p.product_template_id, r.product_product_id,
                           CASE WHEN r.product_product_id IS NULL THEN '1_product' ELSE '0_product_variant' END,
                           '1_product', 'list_price', 'fixed'
                      FROM sale_subscription_pricing p
                      JOIN sale_subscription_plan plan
                        ON plan.id = p.plan_id
                 LEFT JOIN product_product_sale_subscription_pricing_rel r
                        ON r.sale_subscription_pricing_id = p.id
                 RETURNING _upg_pricing_id, id
        """
    )

    mapping = dict(cr.fetchall())
    if mapping:
        util.replace_record_references_batch(cr, mapping, "sale.subscription.pricing", "product.pricelist.item")

    util.merge_model(
        cr,
        "sale.subscription.pricing",
        "product.pricelist.item",
        fields_mapping={
            "price": "fixed_price",
            "product_template_id": "product_tmpl_id",
        },
    )
    util.remove_column(cr, "product_pricelist_item", "_upg_pricing_id")

    util.rename_field(cr, "product.pricelist", "product_subscription_pricing_ids", "subscription_item_ids")
    util.rename_field(cr, "product.template", "product_subscription_pricing_ids", "subscription_rule_ids")
    util.rename_field(cr, "sale.subscription.plan", "product_subscription_pricing_ids", "subscription_rule_ids")
