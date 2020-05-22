# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "product_template", "split_method_landed_cost", "varchar")
    util.create_column(cr, "stock_landed_cost", "target_model", "varchar", default="picking")
