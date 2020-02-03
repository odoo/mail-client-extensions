# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_move", "tax_report_control_error", "boolean")
    util.remove_field(cr, "res.company", "days_between_two_followups")
    util.remove_field(cr, "res.config.settings", "days_between_two_followups")
    util.remove_field(cr, "res.partner", "payment_next_action_date")
    util.remove_field(cr, "res.partner", "unreconciled_aml_ids")
    util.remove_field(cr, "res.partner", "partner_ledger_label")
    util.remove_field(cr, "res.partner", "total_due")
    util.remove_field(cr, "res.partner", "total_overdue")
    util.remove_field(cr, "res.partner", "followup_status")
