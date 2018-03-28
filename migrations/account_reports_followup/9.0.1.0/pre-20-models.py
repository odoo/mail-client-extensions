# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_field(cr, 'account_followup.followup', 'followup_line', 'followup_line_ids')
    util.remove_field(cr, 'account_followup.followup.line', 'email_template_id')

    gone = util.splitlines("""
        latest_followup_date
        latest_followup_level_id
        latest_followup_level_id_without_lit

        payment_amount_due
        payment_amount_overdue
        payment_earliest_due_date
    """)
    for f in gone:
        util.remove_field(cr, 'res.partner', f)

    util.remove_model(cr, 'account_followup.stat')
    util.remove_model(cr, 'account_followup.stat.by.partner')
    util.remove_model(cr, 'account_followup.sending.results')
    util.remove_model(cr, 'account_followup.print')
    util.remove_model(cr, 'report.account_followup.report_followup')
