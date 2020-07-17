# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # ===========================================================
    # Fusion of automatic entry wizards (PR:48651)
    # ===========================================================
    util.rename_field(cr, 'res.company', 'accrual_default_journal_id', 'automatic_entry_default_journal_id')
    util.remove_model(cr, 'account.accrual.accounting.wizard')
    util.remove_model(cr, 'account.transfer.wizard')
    util.remove_column(cr, 'account_move_line', 'account_internal_type')
    util.remove_record(cr, 'account.action_accrual_entry')
    util.remove_record(cr, 'account.action_move_transfer_accounts')
