# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Force update of records that are in noupdate
    # https://github.com/odoo/odoo/commit/ec07e72845a390cdf9cf72ebbbf4369ea92ecfbe#diff-fc2d30fb6c1302f33b139cf66c290cd27a7332f16d1dc75ba35883f82fcf55d2
    util.update_record_from_xml(cr, "hr_expense.group_hr_expense_manager", reset_write_metadata=False)
    for role in "manager approver".split():
        util.update_record_from_xml(cr, f"hr_expense.ir_rule_hr_expense_{role}", reset_write_metadata=False)
        util.update_record_from_xml(cr, f"hr_expense.ir_rule_hr_expense_sheet_{role}", reset_write_metadata=False)
