# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.column_exists(cr, 'account_financial_html_report_line', 'name'):
        cr.execute("""
            SELECT account_financial_html_report_line.*, ir_model_data.name as xmlid, ir_model_data.module as module
          INTO financial_report_lines_v12_bckp
          FROM account_financial_html_report_line
          LEFT JOIN ir_model_data
          ON  ir_model_data.model='account.financial.html.report.line' AND ir_model_data.res_id = account_financial_html_report_line.id
        """)
        cr.execute("""
            SELECT account_tax_account_tag.*, ir_model_data.name as xmlid, ir_model_data.module as module
              INTO account_tax_account_tag_v12_bckp
              FROM account_tax_account_tag
              LEFT JOIN ir_model_data
              ON  ir_model_data.model='account.account.tag' AND ir_model_data.res_id = account_tax_account_tag.account_account_tag_id
        """)
        cr.execute("""
            SELECT id, account_id, refund_account_id
              INTO tax_accounts_v12_bckp
              FROM account_tax
        """)
