# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    for letter in "ABCDE":
        util.remove_record(cr, f"l10n_it_reports.account_financial_report_line_it_ce_{letter}_TOT")
