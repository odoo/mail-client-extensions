# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # become default...
    util.update_record_from_xml(cr, "hr_expense.mt_expense_paid")
    # XXX should all followers follow this type?
    util.delete_unused(cr, "hr_expense.product_product_fixed_cost")
