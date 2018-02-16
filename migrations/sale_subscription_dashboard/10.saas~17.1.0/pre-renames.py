# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    renames = util.splitlines("""
        action_contract_dashboard_report_main
        menu_action_contract_dashboard_report_main
        action_contract_dashboard_report_cohort
        menu_action_contract_dashboard_report_cohort
        action_contract_dashboard_report_detailed
        action_contract_dashboard_report_forecast
        action_contract_dashboard_report_salesman
        menu_action_contract_dashboard_report_salesman
    """)
    for r in renames:
        r = 'sale_subscription_dashboard.' + r
        t = r.replace('contract', 'subscription')
        util.rename_xmlid(cr, r, t)
