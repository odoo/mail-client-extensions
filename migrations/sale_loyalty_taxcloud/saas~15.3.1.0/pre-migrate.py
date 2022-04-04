# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # This field is replaced by `reward_id`
    util.remove_field(cr, "sale.order.line", "coupon_program_id")

    # Migrate `account.move.line` `coupon_program_id`
    util.create_column(cr, "account_move_line", "reward_id", "integer")
    cr.execute(
        """
        UPDATE account_move_line line
           SET reward_id = reward.id
          FROM loyalty_program p
          JOIN loyalty_reward reward
            ON reward.program_id = p.id
         WHERE p._upg_coupon_program_id = line.coupon_program_id
        """
    )
    util.remove_field(cr, "account.move.line", "coupon_program_id")
