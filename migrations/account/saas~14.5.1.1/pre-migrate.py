# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # ===============================================================
    # Use config bar for real config steps (PR:70115)
    # ===============================================================

    util.remove_view(cr, "account.dashboard_onboarding_bill_step")
    util.create_column(cr, "res_company", "account_setup_taxes_state", "varchar", default="not_done")

    # ===============================================================
    # French tax report: carry over tax grid 27 to tax grid 22 (PR: (odoo) 69887 & (enterprise) 17953)
    # ===============================================================
    util.create_column(cr, "account_tax_report_line", "is_carryover_persistent", "bool", default=True)
    util.create_column(cr, "account_tax_report_line", "is_carryover_used_in_balance", "bool")
