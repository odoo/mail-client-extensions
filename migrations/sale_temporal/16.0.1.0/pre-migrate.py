# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "sale_subscription"):
        util.move_field_to_module(cr, "sale.order.line", "pricing_id", "sale_temporal", "sale_subscription")
    else:
        util.remove_field(cr, "sale.order.line", "pricing_id")

    if util.table_exists(cr, "sale_temporal_recurrence"):
        util.create_column(cr, "sale_temporal_recurrence", "active", "boolean", default=True)
