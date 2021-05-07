# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # ===============================================================
    # Use config bar for real config steps (PR:70115)
    # ===============================================================

    util.remove_view(cr, "account_winbooks_import.account_dashboard_onboarding_panel")
    util.remove_view(cr, "account_winbooks_import.onboarding_winbooks_step")
