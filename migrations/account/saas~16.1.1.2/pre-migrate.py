from odoo.upgrade import util


def migrate(cr, version):
    op_map = {
        ("=", True): "=",  # is_off_balance = True   -> account_type = off_balance
        ("=", False): "!=",  # is_off_balance = False  -> account_type != off_balance
        ("!=", True): "!=",  # is_off_balance != True  -> account_type != off_balance
        ("!=", False): "=",  # is_off_balance != False -> account_type = off_balance
    }

    def is_off_balance_adapter(leaf, is_or, negated):
        _left, operator, right = leaf
        if (operator, right) in op_map:
            operator = op_map[(operator, right)]
            right = "off_balance"
        return [("account_type", operator, right)]

    util.update_field_usage(
        cr, "account.account", "is_off_balance", "account_type", domain_adapter=is_off_balance_adapter
    )
    util.remove_field(cr, "account.account", "is_off_balance")
