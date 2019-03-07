# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.convert_field_to_property(
        cr, "hr.salary.rule", "analytic_account_id", type="many2one", target_model="account.analytic.account"
    )
    util.convert_field_to_property(cr, "hr.salary.rule", "account_tax_id", type="many2one", target_model="account.tax")
    util.convert_field_to_property(
        cr, "hr.salary.rule", "account_debit", type="many2one", target_model="account.account"
    )
    util.convert_field_to_property(
        cr, "hr.salary.rule", "account_credit", type="many2one", target_model="account.account"
    )
