# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.drop_workflow(cr, 'crossovered.budget')

    reports = util.splitlines("""
        report_analyticaccountbudget
        report_budget
        report_crossoveredbudget
    """)
    for report in reports:
        util.delete_model(cr, 'report.account_budget.' + report)
        util.remove_view(cr, 'account_budget.' + report)

    wizards = util.splitlines("""
        account.budget.analytic
        account.budget.crossovered.report
        account.budget.crossovered.summary.report
        account.budget.report
    """)
    for w in wizards:
        util.delete_model(cr, w)
