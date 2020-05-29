# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "res.partner", "customer", drop_column=False)
    util.remove_field(cr, "res.partner", "supplier", drop_column=False)

    # Now adapt domains...
    # FIXME what to do if `account` is not installed?
    def adapter(operator, right):
        thruthy_op = "=" if bool(right) else "!="
        operator = ">" if operator == thruthy_op else "="
        return operator, 0

    util.update_field_references(cr, "customer", "customer_rank", only_models=("res.partner",), domain_adapter=adapter)
    util.update_field_references(cr, "supplier", "supplier_rank", only_models=("res.partner",), domain_adapter=adapter)
