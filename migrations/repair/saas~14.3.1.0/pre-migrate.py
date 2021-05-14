# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "repair_order", "description", "varchar")
    util.create_column(cr, "repair_order", "sale_order_id", "int4")

    util.change_field_selection_values(cr, "repair.order", "state", {"invoice_except": "done"})
