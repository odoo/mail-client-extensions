# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "analytic.account_analytic_line_extended_form")
    util.remove_view(cr, "analytic.report_invertedanalyticbalance")
    util.remove_view(cr, "analytic.report_analyticcostledger")
    util.remove_view(cr, "analytic.report_analyticcostledgerquantity")
    util.remove_view(cr, "analytic.report_analyticjournal")
    util.remove_view(cr, "analytic.report_analyticbalance")
