# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    views = util.splitlines("""

        setup_view_company_form
        res_config_settings_view_form_inherit_account_invoicing

        # reports
        report_financial
        report_generalledger
        report_overdue_document
        report_overdue
        report_partnerledger
        report_tax
        report_trialbalance

    """)

    for view in views:
        util.remove_view(cr, "account." + view)
