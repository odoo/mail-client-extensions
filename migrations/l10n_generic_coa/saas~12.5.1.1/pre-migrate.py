# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    renames = dict(l.split() for l in util.splitlines("""
        conf_stk            current_assets
        conf_cas            stock_valuation
        conf_cas_interim1   stock_in
        conf_cas_interim2   stock_out
        conf_a_recv         receivable
        conf_ova            tax_paid
        conf_ncas           non_current_assets
        conf_prepayments    prepayments
        conf_a_pay          payable
        conf_iva            tax_received
        cas                 non_current_liabilities
        conf_a_sale         income
        exchange_fx_income  income_currency_exchange
        conf_cog            cost_of_goods_sold
        exchange_fx_expense expense_currency_exchange
        a_salary_expense    expense_salary
        a_expense_invest    expense_invest
        a_expense_finance   expense_finance
        conf_a_expense      expense
        a_capital           capital
        a_dividends         dividends
    """))

    for old, new in renames.items():
        util.rename_xmlid(cr, "l10n_generic_coa." + old, "l10n_generic_coa." + new)

    cr.execute("""
        SELECT CONCAT(module, '.', name)
          FROM ir_model_data
         WHERE module = 'l10n_generic_coa'
           AND model = 'account.account.template'
           AND name NOT IN %s
    """, [tuple(renames.keys())])
    for account, in cr.fetchall():
        util.remove_record(cr, account)
