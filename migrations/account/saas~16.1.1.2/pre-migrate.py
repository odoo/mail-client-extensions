# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    op_map = {
        ("=", True): "=",  # is_off_balance = True   -> account_type = off_balance
        ("=", False): "!=",  # is_off_balance = False  -> account_type != off_balance
        ("!=", True): "!=",  # is_off_balance != True  -> account_type != off_balance
        ("!=", False): "=",  # is_off_balance != False -> account_type = off_balance
    }

    def is_off_balance_adapter(leaf, is_or, negated):
        left, operator, right = leaf
        if (operator, right) in op_map:
            operator = op_map[(operator, right)]
            right = "off_balance"
        return [("account_type", operator, right)]

    util.adapt_domains(
        cr, "account.account", "is_off_balance", "account_type", adapter=is_off_balance_adapter, force_adapt=True
    )
    util.remove_field(cr, "account.account", "is_off_balance")
