# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "purchase.order.line", "delay_alert")
    util.remove_field(cr, "purchase.order.line", "propagate_date")
    util.remove_field(cr, "purchase.order.line", "propagate_date_minimum_delta")
