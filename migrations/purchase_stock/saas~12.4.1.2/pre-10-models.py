# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "purchase_order_line", "propagate_date_minimum_delta", "int4")
    util.create_column(cr, "purchase_order_line", "propagate_date", "boolean")
    util.create_column(cr, "purchase_order_line", "propagate_cancel", "boolean")
