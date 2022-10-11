# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.journal", "bank_statement_creation_groupby")
    util.remove_view(cr, "account_online_synchronization.account_journal_form_inherit_online_sync")
