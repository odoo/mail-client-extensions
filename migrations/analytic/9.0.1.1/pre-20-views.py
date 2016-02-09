# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    view_list = util.splitlines("""
        account_analytic_line_extended_form
        report_invertedanalyticbalance
        report_analyticcostledger
        report_analyticcostledgerquantity
        report_analyticjournal
        report_analyticbalance
        view_account_analytic_account_tree
    """)
    for view in view_list:
        util.remove_view(cr, "analytic." + view)
