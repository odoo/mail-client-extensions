from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "module_pos_six")
    util.remove_field(cr, "pos.order.line", "origin_order_id")
    util.remove_field(cr, "pos.order.line", "skip_change")

    # In this adapter, "invoiced" state domain is adapted to check for the presence of account_move.
    # The previous "invoiced" state was effectively equivalent to having account_move set.
    # No other states, such as "paid" or "done" or "cancel" could have account_move assigned.
    # Therefore, the check for the "invoiced" state has been replaced with a check for the presence of account_move.
    def state_domain_adapter(leaf, _or, _neg):
        left, op, right = leaf

        if op not in ["=", "!=", "in", "not in"]:
            return [leaf]

        new_left = ".".join([*left.split(".")[:-1], "account_move"])
        new_op = "!=" if op in ["=", "in"] else "="

        if isinstance(right, (list, tuple)) and "invoiced" in right:
            new_right = list(right)
            if len(new_right) > 1:
                new_right.remove("invoiced")
                return ["|" if op == "in" else "&", (left, op, new_right), (new_left, new_op, False)]
            elif len(new_right) == 1:
                return [(new_left, new_op, False)]

        if right == "invoiced":
            return [(new_left, new_op, False)]

        return [leaf]

    util.adapt_domains(cr, "pos.order", "state", "state", adapter=state_domain_adapter)
    util.change_field_selection_values(cr, "pos.order", "state", {"invoiced": "done"})
