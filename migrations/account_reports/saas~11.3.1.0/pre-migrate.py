# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_record(cr, "account_reports.action_account_followup_all")
    util.remove_record(cr, "account_reports.menu_action_followups")
    util.remove_record(cr, "account_reports.followup_logged_action")

    util.remove_view(cr, "account_reports.report_followup_letter")
    util.remove_view(cr, "account_reports.report_followup_all")

    util.remove_model(cr, "account.followup.report.all")
    util.remove_field(cr, "res.partner", "payment_next_action")
    util.remove_field(cr, "res.users", "payment_next_action", drop_column=False)
