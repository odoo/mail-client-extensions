# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # ===============================================================
    # Use config bar for real config steps (PR:70115)
    # ===============================================================

    util.remove_view(cr, "account.dashboard_onboarding_bill_step")
    util.create_column(cr, "res_company", "account_setup_taxes_state", "varchar", default="not_done")
