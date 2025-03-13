from odoo.upgrade import util


def migrate(cr, version):
    has_sale_coupon = has_sale_gift_card = False
    if util.column_exists(cr, "sale_order", "code_promo_program_id"):
        has_sale_coupon = True
    if util.column_exists(cr, "sale_order_line", "gift_card_id"):
        has_sale_gift_card = True

    # New model `sale.order.coupon.points`
    cr.execute(
        """
        CREATE TABLE sale_order_coupon_points (
            -- ORM fields
            id          SERIAL NOT NULL PRIMARY KEY,
            create_uid  integer,
            create_date timestamp without time zone,
            write_uid   integer,
            write_date  timestamp without time zone,
            -- Logic fields
            order_id INTEGER,
            coupon_id INTEGER,
            points FLOAT
        )
        """
    )
    # New field `order_id` on `loyalty.card`
    util.create_column(cr, "loyalty_card", "order_id", "integer")
    # New field `applied_coupon_ids` on `sale.order`
    util.create_m2m(cr, "loyalty_card_sale_order_rel", "loyalty_card", "sale_order")
    # New field `code_enabled_rule_ids` on `sale.order`
    util.create_m2m(cr, "loyalty_rule_sale_order_rel", "loyalty_rule", "sale_order")
    # New fields on `sale.order.line`
    util.create_column(cr, "sale_order_line", "reward_id", "integer")
    util.create_column(cr, "sale_order_line", "coupon_id", "integer")
    util.create_column(cr, "sale_order_line", "reward_identifier_code", "varchar")
    util.create_column(cr, "sale_order_line", "points_cost", "float")

    if has_sale_coupon:
        _migrate_sale_coupon(cr)

    if has_sale_gift_card:
        _migrate_sale_gift_card(cr)

    # Populate `reward_id`, `coupon_id`, `reward_identifier_code` and `points_cost` in `sale_order_lines`
    # Works for both `sale_coupon` and `sale_gift_card`
    query = """
        WITH helper AS (
             SELECT line.id as line_id, r.id as reward_id, c.id as coupon_id,
                    CONCAT(r.id, '_', c.id, '_', line.id) AS code,
                    CASE WHEN p.program_type = 'gift_card' THEN line.price_total / NULLIF(line.product_uom_qty, 0)
                        WHEN LAG(line.id) over (partition by (r.id, c.id)) IS NULL THEN 1
                        ELSE 0
                    END AS points_cost
               FROM sale_order_line line
               JOIN loyalty_reward r
                 ON r.discount_line_product_id = line.product_id
               JOIN loyalty_program p
                 ON p.id = r.program_id
               JOIN loyalty_card c
                 ON c.program_id = p.id
                    -- One of the following join must be valid for a reward to be applied to the order
          LEFT JOIN loyalty_card_sale_order_rel rel
                 ON line.order_id = rel.sale_order_id AND c.id = rel.loyalty_card_id
          LEFT JOIN sale_order_coupon_points points
                 ON line.order_id = points.order_id AND c.id = points.coupon_id
              WHERE {parallel_filter}
                AND (points.id IS NOT NULL OR rel.sale_order_id IS NOT NULL)
        )
        UPDATE sale_order_line line
           SET reward_id=h.reward_id, coupon_id=h.coupon_id,
               reward_identifier_code=h.code, points_cost=h.points_cost
          FROM helper h
         WHERE h.line_id = line.id
        """
    util.explode_execute(cr, query, table="sale_order_line", alias="line")


def _migrate_sale_coupon(cr):
    # Migrate `applied_coupon_ids` o2m -> m2m
    cr.execute(
        """
        INSERT INTO loyalty_card_sale_order_rel (
            loyalty_card_id, sale_order_id
        )
        SELECT c.id, so.id
          FROM loyalty_card c
          JOIN coupon_coupon co
            ON co.id = c._upg_coupon_coupon_id
          JOIN sale_order so
            ON so.id = co.sales_order_id
        """
    )
    # Migrate `order_id` on coupons
    cr.execute(
        """
        UPDATE loyalty_card c
           SET order_id = coupon.order_id
          FROM coupon_coupon coupon
         WHERE coupon.id = c._upg_coupon_coupon_id
        """
    )
    # Create a new loyalty card (with 0 points) for all 'current' applied programs on orders
    cr.execute(
        """
        INSERT INTO loyalty_card (
            program_id, company_id,
            points, code, order_id
        )
        SELECT p.id, p.company_id,
               0, md5(random()::text), rel.sale_order_id
          FROM coupon_program_sale_order_rel rel
          JOIN loyalty_program p
            ON p._upg_coupon_program_id = rel.coupon_program_id
         UNION
        SELECT p.id, p.company_id,
               0, md5(random()::text), so.id
          FROM sale_order so
          JOIN loyalty_program p
            ON p._upg_coupon_program_id = so.code_promo_program_id
        """
    )
    # Add `code_promo_program_id` to `code_enabled_rule_ids`
    cr.execute(
        """
        INSERT INTO loyalty_rule_sale_order_rel (
            loyalty_rule_id, sale_order_id
        )
        SELECT rule.id, o.id
          FROM sale_order o
          JOIN loyalty_program p
            ON p._upg_coupon_program_id = o.code_promo_program_id
          JOIN loyalty_rule rule
            ON rule.program_id = p.id
        """
    )
    # Create point change entries for those new coupons
    cr.execute(
        """
        INSERT INTO sale_order_coupon_points (
            order_id, coupon_id, points
        )
        SELECT c.order_id, c.id, 1
          FROM loyalty_card c
         WHERE c.order_id IS NOT NULL
        """
    )

    # Deleted fields
    util.remove_field(cr, "sale.order", "promo_code")
    util.remove_field(cr, "sale.order", "code_promo_program_id")
    util.remove_field(cr, "sale.order", "no_code_promo_program_ids")
    util.remove_field(cr, "sale.order", "generated_coupon_ids")
    util.remove_field(cr, "loyalty.card", "sales_order_id")
    util.remove_column(cr, "sale_order_line", "is_reward_line")  # Now a computed field
    util.rename_model(cr, "sale.coupon.apply.code", "sale.loyalty.coupon.wizard")
    # Deleted data
    util.remove_view(cr, "sale_loyalty.res_config_settings_view_form")
    util.remove_view(cr, "sale_loyalty.sale_order_view_form")
    util.remove_view(cr, "sale_loyalty.sale_coupon_view_coupon_program_kanban")
    util.remove_view(cr, "sale_loyalty.sale_coupon_program_view_promo_program_form")
    util.remove_view(cr, "sale_loyalty.sale_coupon_program_view_coupon_program_form")
    util.remove_view(cr, "sale_loyalty.sale_coupon_view_form")
    util.remove_view(cr, "sale_loyalty.sale_coupon_view_tree")
    util.remove_view(cr, "sale_loyalty.sale_coupon_apply_code_view_form")


def _migrate_sale_gift_card(cr):
    # Migrate `buy_line_id` to `order_id`
    cr.execute(
        """
        UPDATE loyalty_card c
           SET order_id = sol.order_id
          FROM gift_card gc
          JOIN sale_order_line sol
            ON sol.id = gc.buy_line_id
         WHERE gc.id = c._upg_gift_card_id
        """
    )
    # Migrate sol.buy_line_id to `applied_coupon_ids`
    cr.execute(
        """
        INSERT INTO loyalty_card_sale_order_rel (
            loyalty_card_id, sale_order_id
        )
        SELECT c.id, sol.order_id
          FROM loyalty_card c
          JOIN gift_card gc
            ON gc.id = c._upg_gift_card_id
          JOIN sale_order_line sol
            ON sol.gift_card_id = gc.id
        """
    )
    # Create point change entries
    cr.execute(
        """
        INSERT INTO sale_order_coupon_points (
            order_id, coupon_id, points
        )
        SELECT c.order_id, c.id, line.price_total / line.product_uom_qty
          FROM loyalty_card c
          JOIN gift_card gc
            ON gc.id = c._upg_gift_card_id
          JOIN sale_order_line line
            ON line.id = gc.buy_line_id
         WHERE c.order_id IS NOT NULL
           AND c._upg_gift_card_id IS NOT NULL
           AND line.product_uom_qty > 0
        """
    )

    # Update loyalty cards, cf `_compute_balance`
    cr.execute(
        """
          WITH helper AS (
              SELECT sol.gift_card_id as gc_id,
                     sol.price_unit *
                        (COALESCE(rate_to.rate, 1.0) / COALESCE(rate_from.rate, 1.0)) as cost
                FROM sale_order_line sol
                JOIN gift_card gc
                  ON gc.id = sol.gift_card_id
                JOIN res_company gc_c
                  ON gc_c.id = gc.company_id
           LEFT JOIN LATERAL (
                    SELECT r.rate
                      FROM res_currency_rate r
                     WHERE (r.company_id IS NULL OR r.company_id = sol.company_id)
                       AND r.currency_id = sol.currency_id AND r.name <= sol.create_date
                  ORDER BY r.company_id, r.name DESC
                     LIMIT 1
                ) rate_from
                  ON 1 = 1
           LEFT JOIN LATERAL (
                    SELECT r.rate
                      FROM res_currency_rate r
                     WHERE (r.company_id IS NULL OR r.company_id = gc.company_id)
                       AND r.currency_id = gc_c.currency_id AND r.name <= sol.create_date
                  ORDER BY r.company_id, r.name DESC
                     LIMIT 1
                ) rate_to
                  ON 1 = 1
               WHERE sol.state IN ('sale', 'done')
          )
        UPDATE loyalty_card lc
           SET points = lc.points + cost.total -- total is negative
          FROM (
              SELECT h.gc_id, SUM(h.cost) as total
                FROM helper h
            GROUP BY h.gc_id
          ) cost
          WHERE cost.gc_id = lc._upg_gift_card_id
        """
    )

    # Old `gift_card` data
    util.remove_view(cr, "sale_loyalty.sale_order_view_extend_gift_card_form")
    util.remove_view(cr, "sale_loyalty.sale_gift_card_view_form")
    # Deleted fields
    util.remove_field(cr, "loyalty.card", "buy_line_id")
    util.remove_field(cr, "loyalty.card", "redeem_line_ids")
    util.remove_field(cr, "sale.order", "gift_card_count")
    util.remove_field(cr, "sale.order.line", "gift_card_id")
    util.remove_field(cr, "sale.order.line", "generated_gift_card_ids")
