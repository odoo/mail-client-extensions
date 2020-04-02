# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "account_reports.account_financial_report_detailed_net_profit0")
    util.remove_view(cr, "account_reports.template_coa_table_header")

    cr.execute(
        r"""
        UPDATE account_financial_html_report_line
           SET formulas = regexp_replace(trim(formulas), '(^balance *= *|\.balance\y|;.*)', '', 'g')
    """
    )

    util.remove_field(cr, "account.report", "debit_credit")
