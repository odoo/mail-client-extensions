# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def cleanup(cr):
    modules = ['account_online_sync', 'account_plaid', 'account_yodlee']

    cr.execute("""
        SELECT count(1)
          FROM ir_module_module
         WHERE name = ANY(%s)
           AND state = 'to upgrade'
    """, [modules])
    if cr.fetchone()[0] != 1:
        # there are still modules to upgrade
        return

    util.remove_field(cr, 'account.online.journal', 'institution_id')
    util.delete_model(cr, 'account.institution')

def migrate(cr, version):
    util.rename_field(cr, 'account.bank.statement.line', 'online_id', 'online_identifier')

    util.rename_model(cr, 'online.account', 'account.online.journal')
    # drop it's inherit on mail.thread
    util.remove_field(cr, 'account.online.journal', 'message_last_post')
    cr.execute("DELETE FROM mail_followers WHERE res_model='account.online.journal'")
    cr.execute("DELETE FROM mail_message WHERE model='account.online.journal'")

    util.rename_field(cr, 'account.journal', 'online_account_id', 'account_online_journal_id')

    util.delete_model(cr, 'account.journal.onlinesync.config')

    cleanup(cr)
