# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "default_sale_order_template_id")
    util.create_column(cr, "res_company", "sale_order_template_id", "int4")

    cr.execute(
        """
        WITH defaults AS (
            SELECT def.id AS def_id,
                   def.company_id AS def_cid,
                   tmpl.id as tmpl_id,
                   tmpl.company_id as tmpl_cid
              FROM ir_default def
              JOIN ir_model_fields field ON field.id=def.field_id
              JOIN sale_order_template tmpl on tmpl.id=def.json_value::decimal
             WHERE field.model = 'sale.order'
               AND field.name = 'sale_order_template_id'
               AND def.user_id IS NULL
               AND def.condition IS NULL
               AND jsonb_typeof(def.json_value::jsonb) = 'number'
          ORDER BY def_cid,def_id
        )
        UPDATE res_company comp
           SET sale_order_template_id=tmpl_id
          FROM defaults def
         WHERE comp.sale_order_template_id IS NULL
           AND (def_cid IS NULL OR comp.id = def_cid)
           AND (tmpl_cid IS NULL OR tmpl_cid = def_cid)
    """
    )
    cr.execute(
        """
        DELETE FROM ir_default
        WHERE id IN (
            SELECT def.id
              FROM ir_default def
              JOIN ir_model_fields field ON field.id=def.field_id
              JOIN sale_order_template tmpl on tmpl.id=def.json_value::decimal
             WHERE field.model = 'sale.order'
               AND field.name = 'sale_order_template_id'
               AND def.user_id IS NULL
               AND def.condition IS NULL
               AND jsonb_typeof(def.json_value::jsonb) = 'number'
        )
    """
    )

    price_pl_created = False
    discount_pl_created = False

    # Some precisions about pricelists when the 'discount' option is set
    #  - 'without_discount' means that the discount is separated from the price
    #  - 'with_discount' means that the discount is included in the price

    # use a temporary column to store the link between a price list and the
    # corresponding sale order template
    util.create_column(cr, "product_pricelist", "_tmp_so_template_id", 'integer')

    # get the default currency id as the one from the first companyadded in
    # the database
    cr.execute(
        """
        SELECT currency_id FROM res_company
        WHERE id = (SELECT min(id) FROM res_company)
        """)
    default_currency_id = cr.fetchone()[0]

    # create pricelists and pricelist_items
    cr.execute(
        """
        -- per template and per product, extract the right line to transfer to the pricelist
        -- by getting the lowest discount and then, the highest price.

        -- first extract all the lines with a discount and/or a price
        WITH all_lines AS (
            SELECT  sale_order_template_id, product_id, price_unit, discount
            FROM    sale_order_template_line
            WHERE   discount <> 0 OR price_unit <> 0
            UNION ALL
            SELECT  sale_order_template_id, product_id, price_unit, discount
            FROM    sale_order_template_option
            WHERE   discount <> 0 OR price_unit <> 0
        ),

        -- from all lines
        -- 1. filter out the lines using the same price then defined on the product,
        -- 2. if there are multiple lines using the same product, keep the line with the highest price.
        --    This is not possible to define a pricelist with multiple times the same product.
        --    As heuristic, we choose to keep the line with the highest price in such a case.
        -- 3. If there is a discount on the line, but the line price unit is the product price unit, we set it to 0.
        --    Later on, its used to decide it only needs a discount pricelist, without a fixed price pricelist.
        lines AS (
            SELECT DISTINCT ON (sale_order_template_id, product_id)
                   sale_order_template_id, all_lines.product_id, discount,
                   COALESCE(NULLIF(all_lines.price_unit, original_prices.price_unit), 0) as price_unit
            FROM all_lines
            -- Join to get the original price unit of the products.
            -- This is basically the SQL version of the `product.product.lst_price` compute fields
            -- taking into account the variant attribute extra prices.
            JOIN LATERAL (
                SELECT pp.id as product_id, min(pt.list_price) + sum(coalesce(ptav.price_extra, 0)) as price_unit
                FROM product_product pp
                JOIN product_template pt on pt.id = pp.product_tmpl_id
                LEFT JOIN product_variant_combination pvc ON pp.id = pvc.product_product_id
                LEFT JOIN product_template_attribute_value ptav ON ptav.id = pvc.product_template_attribute_value_id
                WHERE pp.id = all_lines.product_id
                GROUP BY pp.id
            ) AS original_prices ON TRUE
            -- if the price unit on the line is the price unit of the product and there is no discount,
            -- there is no need to create a pricelist for it.
            WHERE all_lines.price_unit <> original_prices.price_unit OR discount <> 0
            ORDER BY
                sale_order_template_id,
                product_id,
                -- order by the maximum price.
                -- if the price_unit is 0 in the template line,
                -- the onchange when selecting the templates gets the product price unit,
                -- hence the COALESCE(NULLIF(...))
                COALESCE(NULLIF(all_lines.price_unit, 0), original_prices.price_unit) * (100 - coalesce(discount, 0)) DESC
        ),

        -- create 'without discount' pricelist when at least one line in the template
        -- `without_discount` means the discount is shown in the quotation to the customer
        -- has a discount

        discount_pricelists AS (
            INSERT INTO product_pricelist
                        (_tmp_so_template_id, name, currency_id, company_id, sequence, active, discount_policy)
            SELECT t.id, t.name, coalesce(min(c.currency_id), %s), t.company_id, 1,  TRUE, 'without_discount'
            FROM lines l
            JOIN        sale_order_template t ON t.id = l.sale_order_template_id
            LEFT JOIN   res_company c ON c.id = t.company_id
            WHERE l.discount <> 0
            GROUP BY t.id
            RETURNING id, _tmp_so_template_id, currency_id, company_id
        ),

        -- create 'with_discount' pricelist when:
        -- `with_discount` means do not show the discount to the customer, but include it in the price unit
        -- 1) there is no discount and at least a price_unit for a line in the template,
        -- 2) OR, there is at least one line with a discount AND a price_unit.

        fixed_price_pricelists AS (
            INSERT INTO product_pricelist
                        (_tmp_so_template_id, name, currency_id, company_id, sequence, discount_policy, active)
            SELECT      t.id, t.name, COALESCE(min(c.currency_id), %s), t.company_id, 1, 'with_discount', max(l.discount) = 0
            FROM lines l
            JOIN        sale_order_template t ON t.id = l.sale_order_template_id
            LEFT JOIN   res_company c ON c.id = t.company_id
            LEFT JOIN  discount_pricelists dp ON dp._tmp_so_template_id = l.sale_order_template_id
            -- The condition to create a new 'fixed price' pricelist is to have at least of price_unit in the template
            -- and then, a discount on the same line OR no 'discount' pricelist associated to the template 
            WHERE l.price_unit <> 0
                AND (l.discount <> 0 OR dp._tmp_so_template_id IS NULL)
            GROUP BY t.id
            RETURNING   id, _tmp_so_template_id, currency_id, company_id
        ),

        -- transfer all the lines to the pricelists
        -- note: as quotation template lines refer to 'product.product', then pricelist items
        -- refer also to 'product.product' and they are created with 'applied_on' filter
        -- set to '0_product_variant'.

        -- first, all the lines with a discount go to the corresponding 'percent pricelist'
        discount_only_lines AS (
            INSERT INTO     product_pricelist_item
                            (pricelist_id, product_id, applied_on, active, currency_id, company_id, base_pricelist_id,
                             base, compute_price, price_discount, percent_price)
            SELECT          pl1.id, l.product_id, '0_product_variant', TRUE, pl1.currency_id, pl1.company_id,
                    CASE WHEN l.price_unit <> 0 THEN pl2.id ELSE NULL END AS base_pricelist_id,
                    CASE WHEN l.price_unit <> 0 THEN 'pricelist' ELSE 'list_price' END AS base,
                    CASE WHEN l.price_unit <> 0 THEN 'formula' ELSE 'percentage' END AS compute_price,
                    CASE WHEN l.price_unit <> 0 THEN l.discount ELSE NULL END AS price_discount,
                    CASE WHEN l.price_unit <> 0 THEN NULL ELSE l.discount END AS percent_price
            FROM            lines l
            JOIN            discount_pricelists pl1 ON pl1._tmp_so_template_id = l.sale_order_template_id
            LEFT JOIN       fixed_price_pricelists pl2 ON pl2._tmp_so_template_id = l.sale_order_template_id
            WHERE           l.discount <> 0
        ),

        -- then, all lines with just a price_unit go to the corresponding:
        -- 1) 'percent pricelist' if one exists
        -- 2) 'fixed price pricelist' otherwise
        price_only_lines AS (
            INSERT INTO     product_pricelist_item
                            (pricelist_id, product_id, fixed_price, applied_on, base, compute_price, active, currency_id, company_id)
            SELECT           COALESCE(dp.id, fp.id) AS pl, l.product_id, l.price_unit, '0_product_variant', 'list_price', 'fixed', TRUE,
                             COALESCE(dp.currency_id, fp.currency_id), COALESCE(dp.company_id, fp.company_id)
            FROM            lines l
            LEFT JOIN       discount_pricelists dp    ON dp._tmp_so_template_id = l.sale_order_template_id
            LEFT JOIN       fixed_price_pricelists fp ON fp._tmp_so_template_id = l.sale_order_template_id
            WHERE           l.price_unit <> 0 AND l.discount = 0
            RETURNING       id
        ),

        -- finally, for all lines with discount AND price_unit, price_units go to the
        -- corresponding 'fixed price pricelist'
        price_and_discount_lines AS (
            INSERT INTO     product_pricelist_item
                            (pricelist_id, product_id, fixed_price, applied_on, base, compute_price, currency_id, company_id, active)
            SELECT           pl.id, l.product_id, l.price_unit, '0_product_variant', 'list_price', 'fixed', pl.currency_id, pl.company_id, TRUE
            FROM            lines l
            JOIN			fixed_price_pricelists pl ON pl._tmp_so_template_id = l.sale_order_template_id
            WHERE           l.price_unit <> 0 AND l.discount <> 0
            RETURNING       id
        )
        -- get the number of pricelist created to know which options to activate
        -- in the database
        SELECT  (
                SELECT COUNT(*)
                FROM   discount_pricelists
                ),
                (
                SELECT COUNT(*)
                FROM   fixed_price_pricelists
                )
        """,
        (default_currency_id, default_currency_id)
    )

    if cr.rowcount > 0:
        row = cr.fetchone()
        discount_pl_created, price_pl_created = row

    if price_pl_created or discount_pl_created:
        env = util.env(cr)
        env.cache.invalidate()

        # force 'pricelist' option if not already set (no need to force the 'discount' option)
        if not env.user.has_group('product.group_product_pricelist'):
            env["res.groups"].browse(util.ref(cr, "base.group_user")).write(
                {"implied_ids": [(4, util.ref(cr, "product.group_product_pricelist"))]}
            )

        # set pricelist "advanced" if some pricelist with discount values have
        # been created
        if discount_pl_created:
            ICP = env["ir.config_parameter"]
            ICP.set_param("product.product_pricelist_setting", "advanced")
            env["res.groups"].browse(util.ref(cr, "base.group_user")).write(
                {"implied_ids": [(4, util.ref(cr, "product.group_sale_pricelist"))]}
            )

        # add a message to the chatter
        util.add_to_migration_reports(
            message="There are no more Sales Prices & Discounts on quotations"
            " templates. Prices & discounts are now on Pricelists (menu "
            "'Sales/Products/Pricelists'). Thank you to check them before "
            "creating new quotes.",
            category='Sale/Quotation Template'
        )

    # clean columns
    util.remove_column(cr, "product_pricelist", "_tmp_so_template_id")
    util.remove_field(cr, "sale.order.template.line", "price_unit")
    util.remove_field(cr, "sale.order.template.line", "discount")
    util.remove_field(cr, "sale.order.template.option", "price_unit")
    util.remove_field(cr, "sale.order.template.option", "discount")
