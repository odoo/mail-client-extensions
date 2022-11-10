# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_consolidation.consolidation_step")
    util.remove_view(cr, "account_consolidation.chart_of_account_step")
    util.remove_view(cr, "account_consolidation.create_period_step")
    util.remove_view(cr, "account_consolidation.account_consolidation_dashboard_onboarding_panel")
