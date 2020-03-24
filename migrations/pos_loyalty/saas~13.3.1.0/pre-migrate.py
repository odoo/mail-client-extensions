# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):

    # RULES
    util.create_column(cr, "loyalty_rule", "rule_domain", "varchar")
    cr.execute(
        """
            UPDATE loyalty_rule
            SET rule_domain = concat('[(''id'', ''='', ', product_id, ')]')
            WHERE rule_type = 'product' and product_id IS NOT NULL
        """
    )
    cr.execute(
        """
            UPDATE loyalty_rule
            SET rule_domain = concat('[(''pos_categ_id'', ''='', ', category_id, ')]')
            WHERE rule_type = 'category' and category_id IS NOT NULL
        """
    )

    util.remove_field(cr, "loyalty.rule", "rule_type")
    util.remove_field(cr, "loyalty.rule", "product_id")
    util.remove_field(cr, "loyalty.rule", "category_id")
    util.remove_field(cr, "loyalty.rule", "cumulative")

    util.rename_field(cr, "loyalty.rule", "pp_product", "points_quantity")
    util.rename_field(cr, "loyalty.rule", "pp_currency", "points_currency")

    # REWARDS
    util.create_column(cr, "loyalty_reward", "discount_type", "varchar")
    util.create_column(cr, "loyalty_reward", "discount_apply_on", "varchar")
    util.create_column(cr, "loyalty_reward", "discount_max_amount", "float8")
    util.create_column(cr, "loyalty_reward", "discount_fixed_amount", "float8")
    util.create_column(cr, "loyalty_reward", "minimum_amount", "float8")
    util.create_m2m(cr, "loyalty_reward_product_product_rel", "loyalty_reward", "product_product")

    cr.execute(
        """
            UPDATE loyalty_reward
            SET discount_type = 'percentage',
                discount_apply_on = 'on_order',
                discount_max_amount = 0
            WHERE reward_type = 'discount'
        """
    )
    cr.execute(
        """
            UPDATE loyalty_reward
            SET reward_type = 'gift',
                gift_product_id = point_product_id,
                point_cost = minimum_points
            WHERE reward_type = 'resale'
        """
    )

    util.remove_field(cr, "loyalty.reward", "point_product_id")
    util.rename_field(cr, "loyalty.reward", "discount", "discount_percentage")

    #PROGRAMS
    cr.execute(
        """
            INSERT INTO loyalty_rule(name, loyalty_program_id, points_quantity, rule_domain)
                SELECT 'Global', lp.id, lp.pp_product, '[]'
                FROM loyalty_program lp
                WHERE lp.pp_product IS NOT NULL and lp.pp_product !=0
        """
    )

    util.rename_field(cr, "loyalty.program", "pp_currency", "points")
    util.remove_field(cr, "loyalty.program", "pp_product")
    util.remove_field(cr, "loyalty.program", "pp_order")
    util.remove_field(cr, "loyalty.program", "rounding")

    #POINTS
    util.convert_field_to_property(cr, "res.partner", "loyalty_points", "float", company_field="coalesce(company_id, (select id from res_company order by id limit 1))")
