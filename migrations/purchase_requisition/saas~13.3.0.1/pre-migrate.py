# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "purchase_requisition_line", "product_description_variants", "varchar")
