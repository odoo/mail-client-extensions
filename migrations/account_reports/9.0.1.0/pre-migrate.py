# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    for field in ["payment_next_action", "payment_next_action_date", "unreconciled_aml_ids"]:
        util.move_field_to_module(cr, "res.partner", field, "account_reports_followup", "account_reports")
