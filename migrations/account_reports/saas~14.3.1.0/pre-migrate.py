# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    # ===============================================================
    # Add control mechanism in reporting (PR: odoo/enterprise#17009)
    # ===============================================================
    util.create_column(cr, 'account_financial_html_report_line', 'control_domain', 'varchar')

    # ===============================================================
    # Multi-VAT tax reports (PR: 17299)
    # ===============================================================
    util.create_column(cr, 'account_financial_html_report', 'country_id', 'int4')
    util.rename_field(cr, 'res.config.settings', 'account_tax_fiscal_country_id', 'account_fiscal_country_id')
    util.remove_field(cr, 'res.company', 'account_tax_original_periodicity_reminder_day')
