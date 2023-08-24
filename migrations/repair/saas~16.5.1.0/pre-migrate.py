# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # Renaming those 2 fields for easier reading
    util.rename_field(cr, "stock.lot", "repair_order_ids", "repair_line_ids")
    util.rename_field(cr, "stock.lot", "repair_order_count", "repair_part_count")
