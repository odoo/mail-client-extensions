# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces
    # ===========================================================
    # Fusion of automatic entry wizards (PR:48651)
    # ===========================================================
    util.rename_field(cr, 'res.company', 'accrual_default_journal_id', 'automatic_entry_default_journal_id')
    util.remove_model(cr, 'account.accrual.accounting.wizard')
    util.remove_model(cr, 'account.transfer.wizard')
    util.remove_column(cr, 'account_move_line', 'account_internal_type')
    util.remove_record(cr, 'account.action_accrual_entry')
    util.remove_record(cr, 'account.action_move_transfer_accounts')

    # ===========================================================
    # Reconciliation model improvements (PR:55031)
    # ===========================================================
    util.create_column(cr, 'account_reconcile_model', 'active', 'boolean', default=True)
    for table in ('account_reconcile_model', 'account_reconcile_model_template'):
        util.create_column(cr, table, 'matching_order', 'varchar', default='old_first')
        util.create_column(cr, table, 'match_text_location_label', 'boolean', default=True)
        util.create_column(cr, table, 'match_text_location_note', 'boolean', default=False)
        util.create_column(cr, table, 'match_text_location_reference', 'boolean', default=False)

    util.remove_view(cr, 'account.report_invoice_document_with_payments')

    # ===========================================================
    # Tour refactor (PR:55624)
    # ===========================================================
    util.rename_field(cr, 'res.company', *eb('account_onboarding_{sample,create}_invoice_state'))
    util.remove_view(cr, 'account.onboarding_sample_invoice_step')
    util.remove_view(cr, 'account.email_compose_onboarding_sample_invoice')
    util.remove_record(cr, 'account.action_open_account_onboarding_sample_invoice')
