# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    if not util.version_gte("16.0"):
        util.if_unchanged(cr, "hr_expense.product_product_fixed_cost", util.update_record_from_xml)
