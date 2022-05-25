# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "hr_expense.product_product_fixed_cost", util.update_record_from_xml)
