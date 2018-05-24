# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "res.company", "min_days_between_followup")
    util.remove_field(cr, "res.config.settings", "min_days_between_followup")

    util.remove_field(cr, "account.move.line", "result")
    util.remove_field(cr, "res.partner", "payment_note")

    util.create_column(cr, "account_followup_followup_line", "manual_action_type_id", "int4")
    cr.execute(
        "UPDATE account_followup_followup_line SET manual_action_type_id=%s WHERE manual_action=true",
        [util.ref(cr, "mail.mail_activity_data_todo")],
    )
