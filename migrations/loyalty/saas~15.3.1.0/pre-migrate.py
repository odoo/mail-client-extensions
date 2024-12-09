import logging

from psycopg2.extras import execute_values

from odoo import modules

from odoo.upgrade import util
from odoo.upgrade.util import json

_logger = logging.getLogger(__name__)

has_loyalty_models = False
has_loyalty_card = False
has_custom_loyalty_fields = False


def migrate(cr, version):
    # Check for any merged module's presence
    has_coupon = has_gift_card = has_pos_loyalty = False
    if util.table_exists(cr, "coupon_program"):
        has_coupon = True
        # Renamed coupon_program translations to ensure their preservation during the merging of models, which occurs prior to the migration of translations.
        cr.execute("UPDATE ir_translation SET name = 'temp_coupon_name' WHERE name = 'coupon.program,name'")
    if util.table_exists(cr, "gift_card"):
        has_gift_card = True
    if util.table_exists(cr, "loyalty_program"):
        has_pos_loyalty = True
        global has_loyalty_models  # noqa: PLW0603
        has_loyalty_models = True
        # In order to safeguard loyalty_program translations from being lost during the merging of models, we opt to rename them prior to the migration process.
        cr.execute("UPDATE ir_translation SET name = 'temp_loyalty_name' WHERE name = 'loyalty.program,name'")
        # Since the old pos_loyalty and loyalty's models share some common name
        #  rename the old tables for the migration
        util.rename_model(cr, "loyalty.program", "pos.loyalty.program")
        util.rename_model(cr, "loyalty.rule", "pos.loyalty.rule")
        util.rename_model(cr, "loyalty.reward", "pos.loyalty.reward")
        # Rename again this time without changing the tables so we keep `loyalty.program` in our env
        util.rename_model(cr, "pos.loyalty.program", "loyalty.program", rename_table=False)
        util.rename_model(cr, "pos.loyalty.rule", "loyalty.rule", rename_table=False)
        util.rename_model(cr, "pos.loyalty.reward", "loyalty.reward", rename_table=False)
        cr.execute("ALTER TABLE loyalty_reward_product_product_rel RENAME TO pos_loyalty_reward_product_product_rel")

    # Create our different tables
    _create_loyalty_tables(cr)

    if has_coupon:
        _change_model_on_manual_fields(cr, "coupon.program", "loyalty.program")
        _change_model_on_manual_fields(cr, "coupon.rule", "loyalty.rule")
        _change_model_on_manual_fields(cr, "coupon.reward", "loyalty.reward")
        _coupon_migrate(cr)
        _move_manual_fields(cr, "coupon_program", "loyalty.program", "_upg_coupon_program_id")
        _move_manual_fields(
            cr, "coupon_rule", "loyalty.rule", "program_id", join=["loyalty_program", "_upg_coupon_rule_id", "id"]
        )
        _move_manual_fields(
            cr, "coupon_reward", "loyalty.reward", "program_id", join=["loyalty_program", "_upg_coupon_reward_id", "id"]
        )
        _move_manual_fields(cr, "coupon_coupon", "loyalty.card", "_upg_coupon_coupon_id")
    if has_gift_card:
        _change_model_on_manual_fields(cr, "gift.card", "loyalty.card")
        _gift_card_migrate(cr)
        _move_manual_fields(cr, "gift_card", "loyalty.card", "_upg_gift_card_id")
    if has_pos_loyalty:
        _pos_loyalty_migrate(cr)
        _move_manual_fields(cr, "pos_loyalty_program", "loyalty.program", "_upg_pos_program_id")
        _move_manual_fields(
            cr,
            "pos_loyalty_rule",
            "loyalty.rule",
            "program_id",
            join=["loyalty_program", "_upg_pos_program_id", "loyalty_program_id"],
        )
        _move_manual_fields(cr, "pos_loyalty_reward", "loyalty.reward", "_upg_pos_loyalty_reward_id")

    if has_custom_loyalty_fields:
        # The standard views of most renamed/merged models are removed
        # and the studio views that inherit them are deleted as well
        # The custom fields and their data are preserved but the view is gone
        util.add_to_migration_reports(
            category="Loyalty, Coupons, and Gift Cards",
            message="Due to a redesign of multiple modules related to "
            "loyalty, coupons, and gift cards in Odoo 16, many views were "
            "replaced, resulting in the possible loss of custom fields in "
            "views. Please verify the new loyalty views and add your custom "
            "fields back if necessary.",
        )


def _check_mapping(mapping):
    return any(k != v for k, v in mapping.items())


def _change_model_on_manual_fields(cr, from_model, to_model):
    global has_custom_loyalty_fields  # noqa: PLW0603
    cr.execute(
        """
        WITH fields AS (
          SELECT f.id,
                 f.name,
                 bool_or(f2.id IS NOT NULL) AS is_colliding
            FROM ir_model_fields f
            JOIN ir_model_data d
              ON d.model = 'ir.model.fields'
             AND d.res_id = f.id
       LEFT JOIN ir_model_fields f2
              ON f.name = f2.name
             AND f2.model = %(to_model)s
           WHERE f.state = 'base'
             AND f.model =  %(from_model)s
        GROUP BY f.id
          HAVING NOT array_agg(d.module::text) && %(standard_modules)s

           UNION

          SELECT f.id,
                 f.name,
                 bool_or(f2.id IS NOT NULL) AS is_colliding
            FROM ir_model_fields f
       LEFT JOIN ir_model_fields f2
              ON f.name = f2.name
             AND f2.model = %(to_model)s
           WHERE f.state = 'manual'
             AND f.model = %(from_model)s
        GROUP BY f.id
        )

        , upd AS (
          UPDATE ir_model_fields f
             SET model_id = m.id,
                 model = m.model
            FROM ir_model m,
                 fields
           WHERE fields.id = f.id
             AND NOT fields.is_colliding
             AND m.model = %(to_model)s
       RETURNING f.id
        )

        SELECT (SELECT count(*) > 0 FROM upd),
               (SELECT array_agg(f.name) FROM fields f WHERE f.is_colliding)

        """,
        {
            "to_model": to_model,
            "from_model": from_model,
            "standard_modules": list(modules.get_modules()),
        },
    )

    has_moved_fields, skipped_fields = cr.fetchone()
    has_custom_loyalty_fields |= has_moved_fields

    if skipped_fields:
        _logger.warning(
            "Skip moving fields `%s` from `%s` to `%s`, already existing in target model",
            skipped_fields,
            from_model,
            to_model,
        )


def _move_manual_fields(cr, from_table, to_model, link_col, join=None):
    to_table = util.table_of_model(cr, to_model)
    # the target table was just created so we cannot have the
    # same manual fields in the target table, but we could have
    # created them in a previous call to this function

    cr.execute(
        """
        WITH fields AS (
          SELECT f.id
            FROM ir_model_fields f
            JOIN ir_model_data d
              ON d.model = 'ir.model.fields'
             AND d.res_id = f.id
           WHERE f.state = 'base'
             AND f.store
             AND f.ttype NOT IN ('one2many', 'many2many')
             AND f.model = %s
        GROUP BY f.id
          HAVING NOT array_agg(d.module::text) && %s

           UNION

          SELECT id
            FROM ir_model_fields
           WHERE state = 'manual'
             AND store
             AND ttype NOT IN ('one2many', 'many2many')
             AND model = %s
        )

        SELECT quote_ident(f.name), c.udt_name
          FROM ir_model_fields f
          JOIN information_schema.columns c
            ON quote_ident(f.name) = c.column_name
           AND c.table_name = %s
          JOIN fields
            ON fields.id = f.id
    """,
        [
            to_model,
            list(modules.get_modules()),
            to_model,
            from_table,
        ],
    )
    custom_cols = cr.fetchall()
    if custom_cols:
        for col_name, col_type in custom_cols:
            util.create_column(cr, to_table, col_name, col_type)
        fill_columns = """
            UPDATE {to_table} t
               SET {columns}
              FROM {from_table} f
            {join}
             WHERE t.{key} = {condition_table2}.id
        """.format(
            to_table=to_table,
            from_table=from_table,
            join="JOIN {} j ON j.{} = f.{}".format(*join) if join else "",
            key=link_col,
            condition_table2="j" if join else "f",
            columns=",".join("{0} = f.{0}".format(col[0]) for col in custom_cols),
        )
        util.explode_execute(cr, fill_columns, table=to_table, alias="t")


def _coupon_migrate(cr):
    # This specific program is incompatible with it's new loyalty version (`loyalty.10_percent_with_code`)
    #  due to the code being linked to rules now instead, a unicity constraint is triggered when loading
    #  the module with demo data.
    util.remove_record(cr, "loyalty.10_percent_auto_applied")
    util.remove_record(cr, "loyalty.10_percent_auto_applied_coupon_reward")
    util.remove_record(cr, "loyalty.10_percent_auto_applied_coupon_rule")
    # The loyalty.* models only exists if pos_loyalty was installed, in case it was not we actually rename the old
    #  models
    global has_loyalty_models, has_loyalty_card  # noqa: PLW0603
    transform_model = lambda cr, model_src, model_dst: util.rename_model(cr, model_src, model_dst, rename_table=False)
    if has_loyalty_models:
        transform_model = lambda cr, model_src, model_dst: util.merge_model(
            cr, model_src, model_dst, drop_table=False, ignore_m2m="*"
        )
    transform_model(cr, "coupon.program", "loyalty.program")
    util.remove_inherit_from_model(cr, "loyalty.program", "coupon.rule")
    util.remove_inherit_from_model(cr, "loyalty.program", "coupon.reward")
    transform_model(cr, "coupon.rule", "loyalty.rule")
    transform_model(cr, "coupon.reward", "loyalty.reward")
    has_loyalty_models = True
    util.rename_model(cr, "coupon.coupon", "loyalty.card", rename_table=False)
    has_loyalty_card = True
    util.rename_model(cr, "coupon.generate.wizard", "loyalty.generate.wizard")
    # loyalty.program
    cr.execute(
        """
        INSERT INTO loyalty_program (
            -- Existing fields
            name, active, sequence,
            limit_usage, max_usage,
            program_type,
            trigger,
            applies_on,
            company_id, currency_id,
            date_to,
            -- ORM fields
            create_uid, create_date, write_uid, write_date,
            -- Migration fields
            _upg_coupon_program_id, _upg_coupon_rule_id, _upg_coupon_reward_id,
            -- New fields
            portal_visible, portal_point_name
        )
        SELECT p.name, p.active, p.sequence,
               not p.maximum_use_number = 0, p.maximum_use_number,
               CASE
                    WHEN p.program_type = 'coupon_program' THEN 'coupons'
                    WHEN p.program_type = 'promotion_program' AND p.promo_code_usage = 'code_needed' THEN 'promo_code'
                    ELSE 'promotion'
               END,
               CASE
                   WHEN p.promo_code_usage = 'code_needed' THEN 'with_code'
                   WHEN p.promo_code_usage IS NULL AND p.program_type = 'coupon_program' THEN 'with_code'
                   ELSE 'auto'
               END,
               CASE WHEN p.promo_applicability = 'on_next_order' THEN 'future' ELSE 'current' END,
               p.company_id, c.currency_id,
               r.rule_date_to,
               p.create_uid, p.create_date, p.write_uid, p.write_date,
               p.id, p.rule_id, p.reward_id,
               FALSE, 'Points'
          FROM coupon_program p
          JOIN res_company c
            ON c.id = p.company_id
          JOIN coupon_rule r
            ON r.id = p.rule_id
     RETURNING _upg_coupon_program_id, id
        """
    )
    mapping = dict(cr.fetchall())
    if mapping and _check_mapping(mapping):
        _remap_translation(cr, old_name="temp_coupon_name", mapping=mapping, new_name="loyalty.program,name")
        util.replace_record_references_batch(cr, mapping, "loyalty.program")
    # loyalty.rule
    cr.execute(
        """
        INSERT INTO loyalty_rule (
            -- Existing fields
            product_domain,
            minimum_qty, minimum_amount,
            minimum_amount_tax_mode,
            -- ORM fields
            create_uid, create_date, write_uid, write_date,
            -- New fields
            program_id, company_id, active,
            reward_point_amount, reward_point_split,
            reward_point_mode,
            code, mode
        )
        SELECT r.rule_products_domain,
               r.rule_min_quantity, r.rule_minimum_amount,
               CASE WHEN r.rule_minimum_amount_tax_inclusion = 'tax_included' THEN 'incl' ELSE 'excl' END,
               r.create_uid, r.create_date, r.write_uid, r.write_date,
               p.id as program_id, p.company_id, cp.active,
               1, FALSE,
               'order',
               cp.promo_code, CASE WHEN cp.promo_code IS NOT NULL AND cp.promo_code != '' THEN 'with_code' else 'auto' END
          FROM coupon_rule r
          JOIN loyalty_program p
            ON p._upg_coupon_rule_id = r.id
          JOIN coupon_program cp
            ON cp.id = p._upg_coupon_program_id
        """
    )
    # Get loyalty.rule mapping
    cr.execute(
        """
        SELECT old_rule.id, rule.id
          FROM coupon_rule old_rule
          JOIN loyalty_program prog
            ON prog._upg_coupon_rule_id = old_rule.id
          JOIN loyalty_rule rule
            ON rule.program_id = prog.id
        """
    )
    mapping = dict(cr.fetchall())
    if mapping and _check_mapping(mapping):
        util.replace_record_references_batch(cr, mapping, "loyalty.rule")
    # loyalty.reward
    cr.execute(
        """
        INSERT INTO loyalty_reward (
            -- Existing fields
            description,
            reward_type,
            reward_product_id, reward_product_qty,
            discount_mode,
            discount,
            discount_applicability,
            discount_max_amount,
            discount_line_product_id,
            -- ORM fields
            create_uid, create_date, write_uid, write_date,
            -- New fields
            active, program_id, company_id,
            required_points, clear_wallet
        )
        SELECT r.reward_description,
               CASE WHEN r.reward_type = 'free_shipping' THEN 'shipping' ELSE r.reward_type END,
               r.reward_product_id, r.reward_product_quantity,
               CASE WHEN r.discount_type = 'percentage' THEN 'percent' ELSE 'per_point' END,
               CASE WHEN r.discount_type = 'percentage' THEN r.discount_percentage ELSE r.discount_fixed_amount END,
               CASE
                WHEN r.discount_apply_on = 'on_order' THEN 'order'
                WHEN r.discount_apply_on = 'cheapest_product' THEN 'cheapest'
                ELSE 'specific'
               END,
               r.discount_max_amount,
               r.discount_line_product_id,
               r.create_uid, r.create_date, r.write_uid, r.write_date,
               p.active, p.id as program_id, p.company_id,
               1, FALSE
          FROM coupon_reward r
          JOIN loyalty_program p
            ON p._upg_coupon_reward_id = r.id
        """
    )
    # Get loyalty.reward mapping
    cr.execute(
        """
        SELECT old_reward.id, reward.id
          FROM coupon_reward old_reward
          JOIN loyalty_program prog
            ON prog._upg_coupon_reward_id = old_reward.id
          JOIN loyalty_reward reward
            ON reward.program_id = prog.id
        """
    )
    mapping = dict(cr.fetchall())
    if mapping and _check_mapping(mapping):
        util.replace_record_references_batch(cr, mapping, "loyalty.reward")
    # loyalty.card
    cr.execute(
        """
        INSERT INTO loyalty_card (
            -- Existing fields
            code,
            expiration_date,
            partner_id, program_id,
            -- ORM fields
            create_uid, create_date, write_uid, write_date,
            -- Migration fields
            _upg_coupon_coupon_id,
            -- New fields
            company_id,
            points
        )
        SELECT c.code,
               CASE
                WHEN COALESCE(cp.validity_duration, 0) > 0
                    THEN c.create_date + INTERVAL '1 day' * cp.validity_duration
                ELSE NULL
               END,
               c.partner_id, p.id,
               c.create_uid, c.create_date, c.write_uid, c.write_date,
               c.id,
               p.company_id,
               CASE WHEN c.state in ('new', 'sent', 'reserved') THEN 1 ELSE 0 END
          FROM coupon_coupon c
          JOIN loyalty_program p
            ON p._upg_coupon_program_id = c.program_id
          JOIN coupon_program cp
            ON cp.id = c.program_id
     RETURNING _upg_coupon_coupon_id, id
        """
    )
    mapping = dict(cr.fetchall())
    if mapping and _check_mapping(mapping):
        util.replace_record_references_batch(cr, mapping, "loyalty.card")

    cr.execute(
        """
        INSERT INTO loyalty_reward_product_product_rel (
            loyalty_reward_id, product_product_id
        )
        SELECT lp.id, rel.product_product_id
          FROM coupon_reward_product_product_rel rel
          JOIN loyalty_program lp
            ON lp._upg_coupon_reward_id = rel.coupon_reward_id
        """
    )

    util.remove_field(cr, "loyalty.program", "validity_duration")
    util.remove_field(cr, "loyalty.program", "promo_applicability")
    util.remove_field(cr, "loyalty.program", "promo_code")
    util.remove_field(cr, "loyalty.program", "rule_id")
    util.remove_field(cr, "loyalty.program", "reward_id")
    util.remove_field(cr, "loyalty.program", "maximum_use_number")
    util.remove_field(cr, "loyalty.program", "promo_code_usage")
    util.remove_field(cr, "loyalty.rule", "rule_date_from")
    util.remove_field(cr, "loyalty.rule", "rule_date_to")
    util.remove_field(cr, "loyalty.rule", "rule_partners_domain")
    util.remove_field(cr, "loyalty.rule", "rule_products_domain")
    util.remove_field(cr, "loyalty.rule", "rule_min_quantity")
    util.remove_field(cr, "loyalty.rule", "rule_minimum_amount")
    util.remove_field(cr, "loyalty.rule", "rule_minimum_amount_tax_inclusion")
    util.remove_field(cr, "loyalty.reward", "reward_description")
    util.remove_field(cr, "loyalty.reward", "discount_type")
    util.remove_field(cr, "loyalty.reward", "discount_percentage")
    util.remove_field(cr, "loyalty.reward", "discount_apply_on")
    util.remove_field(cr, "loyalty.reward", "discount_specific_product_ids", drop_column=False)
    util.remove_field(cr, "loyalty.reward", "discount_fixed_amount")
    util.remove_field(cr, "loyalty.reward", "reward_product_quantity")
    util.remove_field(cr, "loyalty.card", "discount_line_product_id")
    util.remove_field(cr, "loyalty.card", "state")
    util.remove_field(cr, "loyalty.generate.wizard", "template_id")
    util.remove_field(cr, "loyalty.generate.wizard", "has_partner_email")
    util.remove_field(cr, "loyalty.generate.wizard", "partners_domain")
    util.remove_field(cr, "loyalty.generate.wizard", "generation_type")
    util.remove_field(cr, "loyalty.generate.wizard", "nbr_coupons")

    util.remove_model(cr, "report.coupon.report_coupon")
    util.remove_view(cr, "loyalty.report_coupon_i18n")
    util.remove_view(cr, "loyalty.report_coupon")
    util.remove_view(cr, "loyalty.coupon_program_view_promo_program_search")
    util.remove_view(cr, "loyalty.coupon_program_view_promo_program_tree")
    util.remove_view(cr, "loyalty.coupon_program_view_promo_program_form")
    util.remove_view(cr, "loyalty.view_coupon_program_kanban")
    util.remove_view(cr, "loyalty.coupon_program_view_search")
    util.remove_view(cr, "loyalty.coupon_program_view_tree")
    util.remove_view(cr, "loyalty.coupon_program_view_coupon_program_form")
    util.remove_view(cr, "loyalty.coupon_program_view_form_common")
    util.remove_view(cr, "loyalty.coupon_view_form")
    util.remove_view(cr, "loyalty.coupon_view_tree")
    util.remove_view(cr, "loyalty.coupon_generate_view_form")

    util.remove_record(cr, "loyalty.expire_coupon_cron")


def _gift_card_migrate(cr):
    util.change_field_selection_values(cr, "product.template", "detailed_type", {"gift": "service"})
    # Rename gift card model to loyalty.card if it does not exist yet otherwise merge both models
    global has_loyalty_card  # noqa: PLW0602
    transform_model = lambda cr, model_src, model_dst: util.rename_model(cr, model_src, model_dst, rename_table=False)
    if has_loyalty_card:
        transform_model = lambda cr, model_src, model_dst: util.merge_model(
            cr, model_src, model_dst, drop_table=False, ignore_m2m="*"
        )
    transform_model(cr, "gift.card", "loyalty.card")
    # Create a gift card program
    # We need one per company with gift cards
    cr.execute(
        """
        INSERT INTO loyalty_program (
            name, program_type, applies_on, trigger,
            active, company_id, currency_id, sequence,
            portal_visible, portal_point_name, limit_usage
        )
        SELECT 'Gift Cards', 'gift_card', 'future', 'auto',
               TRUE, gc.company_id, c.currency_id, 100,
               FALSE, cu.symbol, FALSE
          FROM (
               SELECT company_id from gift_card group by company_id
            ) gc
          JOIN res_company c
            ON c.id = gc.company_id
          JOIN res_currency cu
            ON cu.id = c.currency_id
     RETURNING id, company_id
        """
    )
    # loyalty.rule
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
    gift_card_product = util.ref(cr, "loyalty.gift_card_product_50")
    if gift_card_product is None:
        util.update_record_from_xml(cr, "loyalty.gift_card_product_50", force_create=True)
        gift_card_product = util.ref(cr, "loyalty.gift_card_product_50")

    execute_values(
        cr._obj,
        cr.mogrify(
            """
            WITH cte AS (
                INSERT INTO loyalty_rule (
                    reward_point_amount, reward_point_mode, reward_point_split,
                    minimum_qty, minimum_amount, minimum_amount_tax_mode,
                    active, program_id, company_id, mode
                )
                VALUES %%s
             RETURNING id
            )
            INSERT INTO loyalty_rule_product_product_rel (
                loyalty_rule_id, product_product_id
            )
            SELECT id, %s
              FROM cte
            """,
            [gift_card_product],
        ).decode(),
        rule_values,
    )
    # loyalty.reward
    gift_card_payment_product = util.ref(cr, "loyalty.pay_with_gift_card_product")
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
    # loyalty.card
    gift_card_program_ids = tuple([program["id"] for program in gift_card_programs])
    if gift_card_program_ids:
        cr.execute(
            """
            INSERT INTO loyalty_card (
                -- Existing fields
                company_id,
                partner_id, points, code, expiration_date,
                -- ORM fields
                create_uid, create_date, write_uid, write_date,
                -- Migration fields
                _upg_gift_card_id,
                -- New fields
                program_id
            )
            SELECT gc.company_id,
                   gc.partner_id, gc.initial_amount, gc.code, gc.expired_date,
                   gc.create_uid, gc.create_date, gc.write_uid, gc.write_date,
                   gc.id,
                   p.id
              FROM gift_card gc
              JOIN loyalty_program p
                ON p.company_id = gc.company_id
               AND p.id IN %s
         RETURNING _upg_gift_card_id, id
            """,
            (gift_card_program_ids,),
        )
        mapping = dict(cr.fetchall())
        if mapping and _check_mapping(mapping):
            util.replace_record_references_batch(cr, mapping, "loyalty.card")

    util.remove_view(cr, "loyalty.gift_card_view_search")
    util.remove_view(cr, "loyalty.gift_card_view_form")
    util.remove_view(cr, "loyalty.gift_card_view_tree")

    util.remove_field(cr, "loyalty.card", "name")
    util.remove_field(cr, "loyalty.card", "state")
    util.remove_field(cr, "loyalty.card", "expired_date")
    util.remove_field(cr, "loyalty.card", "balance")
    util.remove_field(cr, "loyalty.card", "initial_amount")


def _pos_loyalty_migrate(cr):
    # loyalty.program
    cr.execute(
        """
        INSERT INTO loyalty_program (
            -- Existing fields
            name, active, sequence,
            company_id, currency_id,
            program_type, limit_usage,
            applies_on, trigger,
            portal_visible, portal_point_name,
            -- ORM fields
            create_uid, create_date, write_uid, write_date,
            -- Migration fields
            _upg_pos_program_id
        )
        SELECT DISTINCT ON (p.id)
               p.name, p.active, 100,
               c.id, COALESCE(j.currency_id, jc.currency_id, c.currency_id),
               'loyalty', FALSE,
               'both', 'auto',
               TRUE, 'Loyalty Points',
               p.create_uid, p.create_date, p.write_uid, p.write_date,
               p.id
          FROM pos_loyalty_program p
     LEFT JOIN pos_config co
            ON co.loyalty_id = p.id
     LEFT JOIN res_company c
            ON c.id = co.company_id
     LEFT JOIN account_journal j
            ON j.id = co.journal_id
     LEFT JOIN res_company jc
            ON jc.id = j.company_id
     RETURNING _upg_pos_program_id, id
        """
    )
    mapping = dict(cr.fetchall())
    if mapping and _check_mapping(mapping):
        _remap_translation(cr, old_name="temp_loyalty_name", mapping=mapping, new_name="loyalty.program,name")
        util.replace_record_references_batch(cr, mapping, model_src="pos.loyalty.program", model_dst="loyalty.program")
    # loyalty.rule
    # Since rules could previously give points for both units paid and money spent at the same time
    #  we have to do this in two separate queries (2 rules instead of one if necessary)
    cr.execute(
        """
        INSERT INTO loyalty_rule (
            -- Existing fields
            active, program_id,
            company_id, product_domain,
            reward_point_amount, reward_point_mode,
            minimum_qty, minimum_amount, minimum_amount_tax_mode,
            -- ORM fields
            create_uid, create_date, write_uid, write_date,
            -- New fields
            mode
        )
        SELECT p.active, p.id,
               p.company_id, COALESCE(r.rule_domain, '[("available_in_pos", "=", True)]'),
               r.points_quantity, 'unit',
               0, 0, 'incl',
               r.create_uid, r.create_date, r.write_uid, r.write_date,
               'auto'
          FROM pos_loyalty_rule r
          JOIN loyalty_program p
            ON p._upg_pos_program_id = r.loyalty_program_id
         WHERE r.points_quantity > 0
         UNION
        SELECT p.active, p.id,
               p.company_id, COALESCE(r.rule_domain, '[("available_in_pos", "=", True)]'),
               r.points_currency, 'money',
               0, 0, 'incl',
               r.create_uid, r.create_date, r.write_uid, r.write_date,
               'auto'
          FROM pos_loyalty_rule r
          JOIN loyalty_program p
            ON p._upg_pos_program_id = r.loyalty_program_id
         WHERE r.points_currency > 0
         UNION
        SELECT TRUE, p.id,
               p.company_id, '[("available_in_pos", "=", True)]',
               old_p.points, 'money',
               0, 0, 'incl',
               old_p.create_uid, old_p.create_date, old_p.write_uid, old_p.write_date,
               'auto'
          FROM pos_loyalty_program old_p
          JOIN loyalty_program p
            ON p._upg_pos_program_id = old_p.id
        """
    )
    # Get loyalty.rule mapping
    cr.execute(
        """
        SELECT old_rule.id, rule.id
          FROM pos_loyalty_rule old_rule
          JOIN loyalty_program prog
            ON prog._upg_pos_program_id = old_rule.loyalty_program_id
          JOIN loyalty_rule rule
            ON rule.program_id = prog.id
        """
    )
    mapping = dict(cr.fetchall())
    if mapping and _check_mapping(mapping):
        util.replace_record_references_batch(cr, mapping, model_src="pos.loyalty.rule", model_dst="loyalty.rule")
    # loyalty.reward
    cr.execute(
        """
        INSERT INTO loyalty_reward (
            -- Existing fields
            active, program_id, company_id,
            description, reward_type,
            discount,
            discount_mode,
            discount_applicability,
            discount_max_amount, discount_line_product_id,
            reward_product_id, reward_product_qty,
            required_points, clear_wallet,
            -- ORM fields
            create_uid, create_date, write_uid, write_date,
            -- Migration fields
            _upg_pos_loyalty_reward_id
        )
        SELECT p.active, p.id, p.company_id,
               r.name, CASE WHEN r.reward_type = 'gift' THEN 'product' ELSE 'discount' END,
               CASE WHEN r.discount_type = 'percentage' THEN r.discount_percentage ELSE r.discount_fixed_amount END,
               CASE WHEN r.discount_type = 'percentage' THEN 'percent' ELSE 'per_point' END,
               CASE
                WHEN r.discount_apply_on = 'on_order' THEN 'order'
                WHEN r.discount_apply_on = 'cheapest_product' THEN 'cheapest'
                ELSE 'specific'
               END,
               r.discount_max_amount, r.discount_product_id,
               r.gift_product_id, 1,
               r.minimum_points, FALSE,
               r.create_uid, r.create_date, r.write_uid, r.write_date,
               r.id
          FROM pos_loyalty_reward r
          JOIN loyalty_program p
            ON p._upg_pos_program_id = r.loyalty_program_id
     RETURNING _upg_pos_loyalty_reward_id, id
        """
    )
    mapping = dict(cr.fetchall())
    if mapping and _check_mapping(mapping):
        util.replace_record_references_batch(cr, mapping, model_src="pos.loyalty.reward", model_dst="loyalty.reward")
    cr.execute(
        """
        INSERT INTO loyalty_reward_product_product_rel (
            loyalty_reward_id, product_product_id
        )
        SELECT r.id, rel.product_product_id
          FROM pos_loyalty_reward_product_product_rel rel
          JOIN loyalty_reward r
            ON r._upg_pos_loyalty_reward_id = rel.loyalty_reward_id
        """
    )
    # loyalty.card
    # Loyalty points are company dependent
    cr.execute(
        """
        INSERT INTO loyalty_card (
            program_id, company_id,
            partner_id, points,
            code
        )
        SELECT p.id, p.company_id,
               SPLIT_PART(prop.res_id, ',', 2)::int, prop.value_float,
               md5(random()::text) -- Pseudo random code
          FROM ir_model_fields f
          JOIN ir_property prop
            ON prop.fields_id = f.id
          JOIN loyalty_program p
            ON p.company_id = prop.company_id AND p._upg_pos_program_id IS NOT NULL
         WHERE f.name = 'loyalty_points' AND f.model = 'res.partner'
        """
    )
    # Old `pos_loyalty` cleanup
    util.remove_view(cr, "loyalty.pos_config_view_form_inherit_pos_loyalty")
    util.remove_view(cr, "loyalty.view_pos_pos_form")
    util.remove_view(cr, "loyalty.view_partner_property_form")
    util.remove_field(cr, "res.partner", "loyalty_points")
    util.remove_view(cr, "loyalty.view_partner_property_form")


def _create_loyalty_tables(cr):
    # loyalty.program
    cr.execute(
        """
        CREATE TABLE loyalty_program (
            -- ORM fields
            id          SERIAL NOT NULL PRIMARY KEY,
            create_uid  integer,
            create_date timestamp without time zone,
            write_uid   integer,
            write_date  timestamp without time zone,
            -- Migration field helpers, to be removed in post-migrate
            _upg_coupon_program_id INTEGER,
            _upg_coupon_rule_id INTEGER,
            _upg_coupon_reward_id INTEGER,
            _upg_pos_program_id INTEGER,
            -- Logic fields
            name VARCHAR,
            active BOOLEAN,
            sequence INTEGER,
            company_id INTEGER,
            currency_id INTEGER,
            program_type VARCHAR,
            date_to DATE,
            limit_usage BOOLEAN,
            max_usage INTEGER,
            applies_on VARCHAR,
            trigger VARCHAR,
            portal_visible BOOLEAN,
            portal_point_name VARCHAR
        )
        """
    )
    # loyalty.rule
    cr.execute(
        """
        CREATE TABLE loyalty_rule (
            -- ORM fields
            id          SERIAL NOT NULL PRIMARY KEY,
            create_uid  integer,
            create_date timestamp without time zone,
            write_uid   integer,
            write_date  timestamp without time zone,
            -- Logic fields
            active BOOLEAN,
            program_id INTEGER,
            company_id INTEGER,
            product_domain VARCHAR,
            product_category_id INTEGER,
            product_tag_id INTEGER,
            reward_point_amount FLOAT,
            reward_point_split BOOLEAN,
            reward_point_mode VARCHAR,
            minimum_qty INTEGER,
            minimum_amount FLOAT,
            minimum_amount_tax_mode VARCHAR,
            code VARCHAR,
            mode VARCHAR
        )
        """
    )
    util.create_m2m(cr, "loyalty_rule_product_product_rel", "loyalty_rule", "product_product")
    # loyalty.reward
    cr.execute(
        """
        CREATE TABLE loyalty_reward (
            -- ORM fields
            id          SERIAL NOT NULL PRIMARY KEY,
            create_uid  integer,
            create_date timestamp without time zone,
            write_uid   integer,
            write_date  timestamp without time zone,
            -- Migration fields, to be removed in post-migrate
            _upg_pos_loyalty_reward_id INTEGER,
            -- Logic fields
            active BOOLEAN,
            program_id INTEGER,
            company_id INTEGER,
            description VARCHAR,
            reward_type VARCHAR,
            discount FLOAT,
            discount_mode VARCHAR,
            discount_applicability VARCHAR,
            discount_product_domain VARCHAR,
            discount_category_id INTEGER,
            discount_product_tag_id INTEGER,
            discount_max_amount FLOAT,
            discount_line_product_id INTEGER,
            reward_product_id INTEGER,
            reward_product_tag_id INTEGER,
            reward_product_qty INTEGER,
            required_points INTEGER,
            clear_wallet BOOLEAN
        )
        """
    )
    util.create_m2m(cr, "loyalty_reward_product_product_rel", "loyalty_reward", "product_product")
    # loyalty.card
    cr.execute(
        """
        CREATE TABLE loyalty_card (
            -- ORM fields
            id          SERIAL NOT NULL PRIMARY KEY,
            create_uid  integer,
            create_date timestamp without time zone,
            write_uid   integer,
            write_date  timestamp without time zone,
            -- Migration field helpers, to be removed in post-migrate
            _upg_coupon_coupon_id INTEGER,
            _upg_gift_card_id INTEGER,
            -- Logic fields
            program_id INTEGER,
            company_id INTEGER,
            partner_id INTEGER,
            points FLOAT,
            code VARCHAR,
            expiration_date DATE
        )
        """
    )


def _remap_translation(cr, old_name, mapping, new_name):
    # During remapping, unordered records can cause unique constraint failures. To avoid this, the temp_res_id field is used.
    util.create_column(cr, "ir_translation", "temp_res_id", "int4")
    util.explode_execute(
        cr,
        cr.mogrify(
            "UPDATE ir_translation SET temp_res_id = res_id, res_id = NULL WHERE name = %s",
            [old_name],
        ).decode(),
        table="ir_translation",
    )
    queries = [
        cr.mogrify(
            """
        UPDATE ir_translation
           SET res_id = (%s::jsonb->>temp_res_id::text)::int,
               name = %s
         WHERE temp_res_id IN %s
           AND name = %s
        """,
            [json.dumps(chunk_dict), new_name, tuple(chunk_dict), old_name],
        ).decode()
        for chunk_dict in util.chunks(mapping.items(), 5000, dict)
    ]
    util.parallel_execute(cr, queries)
    util.remove_column(cr, "ir_translation", "temp_res_id")
