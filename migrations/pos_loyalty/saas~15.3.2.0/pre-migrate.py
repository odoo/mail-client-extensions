# -*- coding: utf-8 -*-
from psycopg2.extras import execute_values

from odoo.upgrade import util


def migrate(cr, version):
    has_pos_loyalty = has_pos_coupon = has_pos_gift_card = False
    if util.table_exists(cr, "pos_loyalty_program"):
        has_pos_loyalty = True
    if util.column_exists(cr, "coupon_coupon", "source_pos_order_id"):
        has_pos_coupon = True
    if util.column_exists(cr, "gift_card", "buy_pos_order_line_id"):
        has_pos_gift_card = True

    # New fields
    util.create_column(cr, "loyalty_card", "source_pos_order_id", "integer")
    util.rename_field(cr, "pos.order.line", "is_program_reward", "is_reward_line")
    util.create_column(cr, "pos_order_line", "reward_id", "integer")
    util.create_column(cr, "pos_order_line", "coupon_id", "integer")
    util.create_column(cr, "pos_order_line", "reward_identifier_code", "varchar")
    util.create_column(cr, "pos_order_line", "points_cost", "float")

    if has_pos_loyalty:
        _migrate_pos_loyalty(cr)
    if has_pos_coupon:
        _migrate_pos_coupon(cr)
    if has_pos_gift_card:
        _migrate_pos_gift_card(cr)


def _migrate_pos_loyalty(cr):
    # Migrate `loyalty_id` to `loyalty_program_id`
    util.create_column(cr, "pos_config", "loyalty_program_id", "integer")
    cr.execute(
        """
        UPDATE pos_config config
           SET loyalty_program_id = program.id
          FROM loyalty_program program
         WHERE program._upg_pos_program_id = config.loyalty_id
        """
    )
    # Deleted fields
    util.remove_field(cr, "pos.config", "loyalty_id")
    util.remove_field(cr, "pos.order", "loyalty_points")
    util.remove_field(cr, "loyalty.reward", "minimum_amount")
    util.remove_field(cr, "loyalty.reward", "discount_fixed_amount")
    util.remove_field(cr, "loyalty.reward", "discount_specific_product_ids")
    util.remove_field(cr, "loyalty.reward", "discount_apply_on")
    util.remove_field(cr, "loyalty.reward", "discount_percentage")
    util.remove_field(cr, "loyalty.reward", "discount_type")
    util.remove_field(cr, "loyalty.reward", "discount_product_id")
    util.remove_field(cr, "loyalty.reward", "point_cost")
    util.remove_field(cr, "loyalty.reward", "gift_product_id")
    util.remove_field(cr, "loyalty.reward", "minimum_points")
    util.remove_field(cr, "loyalty.reward", "loyalty_program_id")
    util.remove_field(cr, "loyalty.reward", "name")
    util.remove_field(cr, "loyalty.rule", "rule_domain")
    util.remove_field(cr, "loyalty.rule", "points_currency")
    util.remove_field(cr, "loyalty.rule", "points_quantity")
    util.remove_field(cr, "loyalty.rule", "loyalty_program_id")
    util.remove_field(cr, "loyalty.rule", "name")
    util.remove_field(cr, "loyalty.program", "points")
    # Remove views
    util.remove_view(cr, "pos_loyalty.view_partner_property_form")
    util.remove_view(cr, "pos_loyalty.view_pos_pos_form")
    util.remove_view(cr, "pos_loyalty.view_loyalty_program_kanban")
    util.remove_view(cr, "pos_loyalty.view_loyalty_program_tree")
    util.remove_view(cr, "pos_loyalty.view_loyalty_reward_form")
    util.remove_view(cr, "pos_loyalty.view_loyalty_rule_form")
    util.remove_view(cr, "pos_loyalty.view_loyalty_program_search")
    util.remove_view(cr, "pos_loyalty.view_loyalty_program_form")


def _migrate_pos_coupon(cr):
    # Migrate `source_pos_order_id`
    cr.execute(
        """
        UPDATE loyalty_card card
           SET source_pos_order_id = coupon.source_pos_order_id
          FROM coupon_coupon coupon
         WHERE coupon.id = card._upg_coupon_coupon_id
        """
    )
    # Migrate `promo_barcode`
    util.create_column(cr, "loyalty_rule", "promo_barcode", "varchar")
    cr.execute(
        """
        UPDATE loyalty_rule rule
           SET promo_barcode = coupon_program.promo_barcode
          FROM loyalty_program program
          JOIN coupon_program coupon_program
            ON coupon_program.id = program._upg_coupon_program_id
         WHERE program.id = rule.program_id AND coupon_program.promo_barcode IS NOT NULL
        """
    )
    # Migrate `program_ids` -> 2 many2many
    util.create_m2m(cr, "pos_config_coupon_program_rel", "pos_config", "loyalty_program")
    util.create_m2m(cr, "pos_config_promo_program_rel", "pos_config", "loyalty_program")
    tables = ["pos_config_coupon_program_rel", "pos_config_promo_program_rel"]
    program_types = ["coupons", "promotion"]
    for table, program_type in zip(tables, program_types):
        cr.execute(
            """
            INSERT INTO %s (
                pos_config_id, loyalty_program_id
            )
            SELECT rel.pos_config_id, program.id
              FROM coupon_program_pos_config_rel rel
              JOIN loyalty_program program
                ON program._upg_coupon_program_id = rel.coupon_program_id
             WHERE program.program_type = '%s'
            """
            % (table, program_type)
        )
    # Populate `reward_id`, `reward_identifier_code` and `points_cost`
    cr.execute(
        """
        ALTER TABLE pos_order_line RENAME COLUMN coupon_id TO _upg_coupon_coupon_id
        """
    )
    util.create_column(cr, "pos_order_line", "coupon_id", "integer")
    cr.execute(
        """
        UPDATE pos_order_line line
           SET reward_id = reward.id, coupon_id = card.id,
               reward_identifier_code = CONCAT(reward.id, '_', card.id)
          FROM pos_order_line other_line
          JOIN loyalty_program program
            ON program._upg_coupon_program_id = other_line.program_id
          JOIN loyalty_reward reward
            ON reward.program_id = program.id
          JOIN loyalty_card card
            ON card._upg_coupon_coupon_id = other_line._upg_coupon_coupon_id
         WHERE line.is_reward_line = TRUE AND other_line.id = line.id
        """
    )
    cr.execute(
        """
        ALTER TABLE pos_order_line DROP COLUMN _upg_coupon_coupon_id
        """
    )
    # Removed fields
    util.remove_field(cr, "pos.order", "applied_program_ids")
    util.remove_field(cr, "pos.order", "used_coupon_ids")
    util.remove_field(cr, "pos.order", "generated_coupon_ids")
    util.remove_field(cr, "pos.config", "program_ids")
    util.remove_field(cr, "pos.order.line", "program_id")
    util.remove_field(cr, "loyalty.card", "pos_order_id")
    # Old data
    util.remove_view(cr, "loyalty.view_pos_pos_form")
    util.remove_view(cr, "pos_loyalty.res_config_view_form_inherit_pos_coupon")
    util.remove_view(cr, "pos_loyalty.pos_coupon_pos_config_view_form")
    util.remove_view(cr, "pos_loyalty.pos_coupon_program_view_promo_program_form")
    util.remove_view(cr, "pos_loyalty.pos_coupon_program_view_coupon_program_form")
    util.remove_view(cr, "pos_loyalty.pos_coupon_view_form")


def _migrate_pos_gift_card(cr):
    # New field `gift_card_program_id`
    util.create_column(cr, "pos_config", "gift_card_program_id", "integer")
    # Migrate from `gift_card_product_id` to `gift_card_program_id`
    # Since we could previously set any product as 'gift card' in pos, we have to create
    #  a program matching that product if it does not exist yet
    cr.execute(
        """
        SELECT min(config.id) as id, config.gift_card_product_id as product
          FROM pos_config config
     LEFT JOIN loyalty_rule_product_product_rel rel
            ON rel.product_product_id = config.gift_card_product_id
     LEFT JOIN loyalty_rule rule
            ON rule.id = rel.loyalty_rule_id
     LEFT JOIN loyalty_program program
            ON program.id = rule.program_id
         WHERE config.gift_card_product_id IS NOT NULL
           AND (rel.product_product_id IS NULL
               OR program.program_type != 'gift_card')
      GROUP BY config.gift_card_product_id
        """
    )
    invalid_configs = cr.dictfetchall()
    if invalid_configs:
        invalid_config_ids = tuple(res["id"] for res in invalid_configs)
        cr.execute(
            """
            INSERT INTO loyalty_program (
                name, program_type, applies_on, trigger,
                active, company_id, currency_id, sequence,
                portal_visible, portal_point_name, limit_usage
            )
            SELECT 'Gift Cards', 'gift_card', 'future', 'auto',
                   TRUE, config.company_id, company.currency_id, 100,
                   FALSE, currency.symbol, FALSE
              FROM pos_config config
              JOIN res_company company
                ON company.id = config.company_id
              JOIN res_currency currency
                ON currency.id = company.currency_id
             WHERE config.id in %s
         RETURNING id, company_id
            """,
            (invalid_config_ids,),
        )
        gift_card_programs = cr.dictfetchall()
        rule_values = [
            (
                1,
                "money",
                True,
                0,
                0,
                "incl",
                True,
                program["id"],
                program["company_id"],
                "auto",
            )
            for program in gift_card_programs
        ]
        execute_values(
            cr._obj,
            """
            INSERT INTO loyalty_rule (
                reward_point_amount, reward_point_mode, reward_point_split,
                minimum_qty, minimum_amount, minimum_amount_tax_mode,
                active, program_id, company_id, mode
            )
            VALUES %s
         RETURNING id
            """,
            rule_values,
        )
        rules = cr.dictfetchall()
        rel_values = [(config["product"], rule["id"]) for config, rule in zip(invalid_configs, rules)]
        execute_values(
            cr._obj,
            """
            INSERT INTO loyalty_rule_product_product_rel (
                product_product_id, loyalty_rule_id
            )
            VALUES %s
            """,
            rel_values,
        )
        env = util.env(cr)
        gift_card_payment_product = env.ref("loyalty.pay_with_gift_card_product", raise_if_not_found=False).id
        reward_values = [
            (
                "discount",
                "per_point",
                1,
                "order",
                1,
                True,
                program["id"],
                program["company_id"],
                "Pay With Gift Card",
                gift_card_payment_product,
                False,
            )
            for program in gift_card_programs
        ]
        execute_values(
            cr._obj,
            """
            INSERT INTO loyalty_reward (
                reward_type, discount_mode, discount, discount_applicability,
                required_points,
                active, program_id, company_id,
                description, discount_line_product_id, clear_wallet
            )
            VALUES %s
            """,
            reward_values,
        )

    # Assign `gift_card_program_id` as we now guarantee to have a program associated with
    #  the old gift card
    cr.execute(
        """
        UPDATE pos_config config
           SET gift_card_program_id = program.id
          FROM loyalty_program program
          JOIN loyalty_rule rule
            ON rule.program_id = program.id
          JOIN loyalty_rule_product_product_rel rel
            ON rel.loyalty_rule_id = rule.id
         WHERE config.gift_card_product_id = rel.product_product_id
        """
    )

    # Update loyalty cards, cf `_compute_balance`
    cr.execute(
        """
          WITH helper AS (
              SELECT psol.gift_card_id as gc_id,
                     psol.price_unit *
                        (COALESCE(rate_to.rate, 1.0) / COALESCE(rate_from.rate, 1.0)) as cost
                FROM pos_order_line psol
                JOIN pos_order po
                  ON po.id = psol.order_id
                JOIN res_company po_c
                  ON po_c.id = po.company_id
                JOIN gift_card gc
                  ON gc.id = psol.gift_card_id
                JOIN res_company gc_c
                  ON gc_c.id = gc.company_id
           LEFT JOIN LATERAL (
                    SELECT r.rate
                      FROM res_currency_rate r
                     WHERE (r.company_id IS NULL OR r.company_id = psol.company_id)
                       AND r.currency_id = po_c.currency_id AND r.name <= psol.create_date
                  ORDER BY r.company_id, r.name DESC
                     LIMIT 1
                ) rate_from
                  ON 1 = 1
           LEFT JOIN LATERAL (
                    SELECT r.rate
                      FROM res_currency_rate r
                     WHERE (r.company_id IS NULL OR r.company_id = gc.company_id)
                       AND r.currency_id = gc_c.currency_id AND r.name <= psol.create_date
                  ORDER BY r.company_id, r.name DESC
                     LIMIT 1
                ) rate_to
                  ON 1 = 1
               WHERE po.state IN ('invoiced', 'done', 'paid')
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

    # Migrate `buy_pos_order_line_id`
    cr.execute(
        """
        UPDATE loyalty_card c
           SET source_pos_order_id = line.order_id
          FROM gift_card gc
          JOIN pos_order_line line
            ON line.id = gc.buy_pos_order_line_id
         WHERE gc.id = c._upg_gift_card_id
        """
    )
    # Populate `reward_id`, `coupon_id`, `reward_identifier_code`, `points_cost`
    cr.execute(
        """
        UPDATE pos_order_line line
           SET reward_id = reward.id, coupon_id = card.id,
               reward_identifier_code = CONCAT(reward.id, '_', card.id),
               points_cost = line.price_subtotal_incl
          FROM loyalty_card card
          JOIN loyalty_reward reward
            ON reward.program_id = card.program_id
         WHERE card._upg_gift_card_id = line.gift_card_id
        """
    )

    # Removed field
    util.remove_field(cr, "loyalty.card", "buy_pos_order_line_id")
    util.remove_field(cr, "loyalty.card", "redeem_pos_order_line_ids")
    util.remove_field(cr, "pos.config", "gift_card_product_id")
    util.remove_field(cr, "pos.order", "gift_card_count")
    util.remove_field(cr, "pos.order.line", "gift_card_id")
    util.remove_field(cr, "pos.order.line", "generated_gift_card_ids")
    # Old data
    util.remove_view(cr, "pos_loyalty.res_config_view_form_inherit_pos_coupon")
    util.remove_view(cr, "pos_loyalty.pos_gift_card_config_view_form")
