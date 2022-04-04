# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "loyalty_program", "_upg_coupon_program_id")
    util.remove_column(cr, "loyalty_program", "_upg_coupon_rule_id")
    util.remove_column(cr, "loyalty_program", "_upg_coupon_reward_id")
    util.remove_column(cr, "loyalty_program", "_upg_pos_program_id")
    util.remove_column(cr, "loyalty_reward", "_upg_pos_loyalty_reward_id")
    util.remove_column(cr, "loyalty_card", "_upg_coupon_coupon_id")
    util.remove_column(cr, "loyalty_card", "_upg_gift_card_id")
    tables_to_clean = [
        "coupon_program",
        "coupon_rule",
        "coupon_reward",
        "coupon_coupon",
        "gift_card",
        "pos_loyalty_program",
        "pos_loyalty_rule",
        "pos_loyalty_reward",
    ]
    for table in tables_to_clean:
        for m2m in util.get_m2m_tables(cr, table):
            cr.execute("DROP TABLE %s CASCADE" % (m2m,))
    tables_to_drop = [
        "coupon_program",
        "coupon_rule",
        "coupon_reward",
        "coupon_coupon",
        "gift_card",
        "pos_loyalty_program",
        "pos_loyalty_rule",
        "pos_loyalty_reward",
        "pos_loyalty_reward_product_product_rel",
    ]
    for table in tables_to_drop:
        cr.execute("DROP TABLE IF EXISTS %s CASCADE" % (table,))
