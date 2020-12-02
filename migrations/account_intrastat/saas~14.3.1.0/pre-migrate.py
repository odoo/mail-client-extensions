# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "product_product", "intrastat_variant_id", "int4")
