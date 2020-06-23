# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_company", "account_revaluation_journal_id", "int4")
    util.create_column(cr, "res_company", "account_revaluation_expense_provision_account_id", "int4")
    util.create_column(cr, "res_company", "account_revaluation_income_provision_account_id", "int4")
