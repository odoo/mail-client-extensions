# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_reports.report_journal")
    util.remove_model(cr, "account.consolidated.journal")
    util.remove_record(cr, "account_reports.action_account_report_cj")
    util.remove_menus(
        cr,
        [
            util.ref(cr, "account_reports.menu_action_account_report_cj"),
            util.ref(cr, "account_reports.menu_print_journal"),
        ],
    )
