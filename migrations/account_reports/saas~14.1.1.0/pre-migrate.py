# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr, "account_intrastat.action_account_report_sales", "account_reports.action_account_report_sales"
    )
    util.rename_xmlid(
        cr, "account_intrastat.menu_action_account_report_sales", "account_reports.menu_action_account_report_sales"
    )
    util.move_model(cr, "account.sales.report", "account_intrastat", "account_reports")
