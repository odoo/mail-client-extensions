# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "stock_warn_insufficient_qty_repair", "quantity", "float8")
    util.create_column(cr, "stock_warn_insufficient_qty_repair", "product_uom_name", "varchar")
