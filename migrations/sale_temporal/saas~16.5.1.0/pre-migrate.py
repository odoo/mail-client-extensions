# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "sale_subscription"):
        util.move_field_to_module(cr, "sale.order", "internal_note", "sale_temporal", "sale_subscription")
    else:
        util.remove_field(cr, "sale.order", "internal_note")
    util.remove_view(cr, "sale_temporal.sale_subscription_order_view_form")
