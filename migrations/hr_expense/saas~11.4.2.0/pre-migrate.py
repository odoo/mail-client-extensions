# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "module_sale_expense")

    util.rename_xmlid(cr, "hr_expense.property_rule_expense_manager", "hr_expense.ir_rule_hr_expense_manager")
    util.rename_xmlid(cr, "hr_expense.property_rule_expense_employee", "hr_expense.ir_rule_hr_expense_employee")
