# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    views = util.splitlines("""

        setup_view_company_form
        res_config_settings_view_form_inherit_account_invoicing
        product_template_form_view_invoice_policy

        # reports
        report_financial
        report_generalledger
        report_overdue_document
        report_overdue
        report_partnerledger
        report_tax
        report_trialbalance
        account_report_general_ledger_view

    """)

    for view in views:
        util.remove_view(cr, "account." + view)
