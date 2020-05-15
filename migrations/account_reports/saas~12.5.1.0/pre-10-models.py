# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_move", "tax_report_control_error", "boolean")
    util.remove_field(cr, "res.company", "days_between_two_followups")
    util.remove_field(cr, "res.config.settings", "days_between_two_followups")
    util.remove_field(cr, "res.partner", "partner_ledger_label")

    partner_fields = {
        "payment_next_action_date",
        "unreconciled_aml_ids",
        "total_due",
        "total_overdue",
        "followup_status",
    }

    if util.module_installed(cr, "account_followup"):
        for field in partner_fields:
            util.move_field_to_module(cr, "res.partner", field, "account_reports", "account_followup")
        util.move_model(cr, "account.followup.report", "account_reports", "account_followup")
        util.move_field_to_module(cr, "account.report.manager", "partner_id", "account_reports", "account_followup")
    else:
        for field in partner_fields:
            util.remove_field(cr, "res.partner", field)
        util.remove_model(cr, "account.followup.report")
        util.remove_field(cr, "account.report.manager", "partner_id")
