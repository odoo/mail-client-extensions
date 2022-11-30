# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "product.label.layout", "move_line_ids")
    cr.execute("DROP TABLE IF EXISTS product_label_layout_stock_move_line_rel")
