# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_field(cr, 'account.bank.statement.line', 'online_id', 'online_identifier')

    util.rename_model(cr, 'online.account', 'account.online.journal')
    # drop it's inherit on mail.thread
    util.remove_field(cr, 'account.online.journal', 'message_last_post')
    cr.execute("DELETE FROM mail_followers WHERE res_model='account.online.journal'")
    cr.execute("DELETE FROM mail_message WHERE model='account.online.journal'")

    util.rename_field(cr, 'account.journal', 'online_account_id', 'account_online_journal_id')

    util.delete_model(cr, 'account.journal.onlinesync.config')
