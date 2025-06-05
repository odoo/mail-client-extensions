from odoo.upgrade import util


def migrate(cr, version):
    if util.column_exists(cr, "product_template", "service_tracking"):
        util.move_field_to_module(cr, "product.template", "service_tracking", "sale", "product")
    else:
        util.create_column(cr, "product_template", "service_tracking", "varchar", default="no")
    util.delete_unused(cr, "product.group_sale_pricelist")
    util.remove_field(cr, "res.config.settings", "group_sale_pricelist")
    util.remove_field(cr, "res.config.settings", "product_pricelist_setting")

    formula_query = util.explode_query_range(
        cr,
        """
        UPDATE product_pricelist_item item
           SET compute_price = 'percentage',
               percent_price = item.price_discount
          FROM product_pricelist pp
         WHERE pp.id = item.pricelist_id
           AND item.compute_price = 'formula'
           AND pp.discount_policy = 'without_discount'
           AND COALESCE(item.price_surcharge, 0) = 0
           AND COALESCE(item.price_round, 0) = 0
           AND COALESCE(item.price_min_margin, 0) = 0
           AND COALESCE(item.price_max_margin, 0) = 0
           AND {parallel_filter}
        """,
        table="product_pricelist_item",
        alias="item",
    )
    percentage_query = util.explode_query_range(
        cr,
        """
        UPDATE product_pricelist_item item
           SET compute_price = 'formula',
               price_discount = item.percent_price
          FROM product_pricelist pp
         WHERE pp.id = item.pricelist_id
           AND item.compute_price = 'percentage'
           AND pp.discount_policy = 'with_discount'
           AND {parallel_filter}
        """,
        table="product_pricelist_item",
        alias="item",
    )
    util.parallel_execute(cr, formula_query + percentage_query)

    util.remove_field(cr, "product.pricelist", "discount_policy")

    util.create_column(cr, "product_pricelist_item", "price_markup", "float8")
    util.explode_execute(
        cr,
        """
        UPDATE product_pricelist_item
           SET price_markup = -price_discount
         WHERE base = 'standard_price'
        """,
        table="product_pricelist_item",
    )
    util.create_column(cr, "product_pricelist_item", "display_applied_on", "varchar", default="1_product")
    util.explode_execute(
        cr,
        """
        UPDATE product_pricelist_item
           SET display_applied_on = '2_product_category'
         WHERE applied_on = '2_product_category'
        """,
        table="product_pricelist_item",
    )
