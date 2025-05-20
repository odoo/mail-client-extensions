from odoo.upgrade import util


def migrate(cr, version):
    def is_done_adapter(leaf, _or, _neg):
        _, op, right = leaf
        if op == "!=":
            right = not right
        new_op = "in" if right else "not in"
        return [("state", new_op, ("done", "cancel"))]

    util.update_field_usage(cr, "stock.move", "is_done", "state", domain_adapter=is_done_adapter)
    util.remove_field(cr, "stock.move", "is_done")
